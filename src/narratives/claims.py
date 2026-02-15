"""
Hierarchical Claim Architecture: DAG of economic propositions with influence scoring.

Each claim is a one-sentence economic proposition. Claims form a directed acyclic
graph where edges represent causal dependency. Nodes are ranked by influence
magnitude — the degree to which each claim propagates consequences through the
financial system.
"""

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class ClaimTier(Enum):
    """Ordinal influence tier (avoids false precision of cardinal scores)."""

    TIER_1 = "tier_1"  # Root-level macro drivers
    TIER_2 = "tier_2"  # First/second-order consequences
    TIER_3 = "tier_3"  # Downstream / observable effects


class CausalDirection(Enum):
    """Whether the causal direction between two claims is established or disputed."""

    ESTABLISHED = "established"
    DISPUTED = "disputed"


@dataclass
class Claim:
    """A single economic proposition in the claim hierarchy."""

    id: str
    text: str  # One-sentence economic claim
    parent_ids: List[str] = field(default_factory=list)
    child_ids: List[str] = field(default_factory=list)
    asset_classes: List[str] = field(default_factory=list)  # e.g. Rates, FX, Equities
    related_assets: List[str] = field(default_factory=list)  # e.g. NVDA, EUR/USD
    tier: ClaimTier = ClaimTier.TIER_3

    # Influence metrics (computed by ClaimGraph)
    influence_score: float = 0.0  # 0-100 scale
    descendant_count: int = 0
    depth: int = 0  # 0 = root

    # Temporal properties
    created_at: Optional[datetime] = None
    persistence_days: int = 0  # How long this claim has been active
    expected_duration: str = ""  # e.g. "structural", "transient", "cyclical"
    trend: str = "stable"  # "rising", "stable", "fading"

    # Edge metadata (to parent)
    causal_direction: CausalDirection = CausalDirection.ESTABLISHED


@dataclass
class CrossTreeInteraction:
    """Where two independent root claims create opposing pressures on the same asset."""

    asset: str
    claim_a_id: str
    claim_a_root_id: str
    claim_a_text: str
    claim_a_signal: str  # e.g. "sell", "buy", "neutral"
    claim_b_id: str
    claim_b_root_id: str
    claim_b_text: str
    claim_b_signal: str
    description: str = ""


class ClaimGraph:
    """
    Manages a DAG of economic claims and computes influence scores.

    Influence magnitude uses causal breadth (descendant count) combined with
    depth (root claims rank highest). As the dataset grows, this can graduate
    to weighted PageRank.
    """

    def __init__(self) -> None:
        self.claims: Dict[str, Claim] = {}

    # ── Mutation ──────────────────────────────────────────────────────────────

    def add_claim(self, claim: Claim) -> None:
        """Add a claim to the graph."""
        self.claims[claim.id] = claim

    def add_edge(
        self,
        parent_id: str,
        child_id: str,
        direction: CausalDirection = CausalDirection.ESTABLISHED,
    ) -> None:
        """Add a causal edge from parent to child."""
        parent = self.claims.get(parent_id)
        child = self.claims.get(child_id)
        if parent is None or child is None:
            return
        if child_id not in parent.child_ids:
            parent.child_ids.append(child_id)
        if parent_id not in child.parent_ids:
            child.parent_ids.append(parent_id)
        child.causal_direction = direction

    # ── Queries ───────────────────────────────────────────────────────────────

    def get_roots(self) -> List[Claim]:
        """Return all root claims (no parents)."""
        return [c for c in self.claims.values() if not c.parent_ids]

    def get_children(self, claim_id: str) -> List[Claim]:
        """Return direct children of a claim."""
        claim = self.claims.get(claim_id)
        if claim is None:
            return []
        return [self.claims[cid] for cid in claim.child_ids if cid in self.claims]

    def get_parents(self, claim_id: str) -> List[Claim]:
        """Return direct parents of a claim."""
        claim = self.claims.get(claim_id)
        if claim is None:
            return []
        return [self.claims[pid] for pid in claim.parent_ids if pid in self.claims]

    def get_subtree_ids(self, claim_id: str) -> Set[str]:
        """Return all descendant IDs of a claim (BFS)."""
        visited: Set[str] = set()
        queue: deque[str] = deque()
        claim = self.claims.get(claim_id)
        if claim is None:
            return visited
        for cid in claim.child_ids:
            queue.append(cid)
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            node = self.claims.get(current)
            if node:
                for cid in node.child_ids:
                    if cid not in visited:
                        queue.append(cid)
        return visited

    def get_claim(self, claim_id: str) -> Optional[Claim]:
        """Get a claim by ID."""
        return self.claims.get(claim_id)

    # ── Influence scoring ─────────────────────────────────────────────────────

    def compute_influence(self) -> None:
        """
        Compute influence scores for all claims.

        Algorithm: depth + breadth.
        - depth_score = 1 / (1 + depth)  — roots score highest
        - breadth_score = descendant_count / max_descendants  — more descendants = more influence
        - influence = 0.5 * depth_score + 0.5 * breadth_score  (scaled to 0-100)

        Also assigns tiers:
        - depth 0 → Tier 1
        - depth 1-2 → Tier 2
        - depth 3+ → Tier 3
        """
        if not self.claims:
            return

        # 1. Compute depth via BFS from roots
        roots = self.get_roots()
        for claim in self.claims.values():
            claim.depth = 0
            claim.descendant_count = 0

        visited: Set[str] = set()
        queue: deque[Tuple[str, int]] = deque()
        for root in roots:
            queue.append((root.id, 0))

        while queue:
            cid, d = queue.popleft()
            if cid in visited:
                continue
            visited.add(cid)
            node = self.claims.get(cid)
            if node is None:
                continue
            node.depth = d
            for child_id in node.child_ids:
                if child_id not in visited:
                    queue.append((child_id, d + 1))

        # 2. Compute descendant counts
        for claim in self.claims.values():
            claim.descendant_count = len(self.get_subtree_ids(claim.id))

        max_desc = max(
            (c.descendant_count for c in self.claims.values()), default=1
        )
        if max_desc == 0:
            max_desc = 1

        # 3. Compute influence scores
        for claim in self.claims.values():
            depth_score = 1.0 / (1.0 + claim.depth)
            breadth_score = claim.descendant_count / max_desc
            claim.influence_score = round(
                (0.5 * depth_score + 0.5 * breadth_score) * 100, 1
            )

            # Assign tiers
            if claim.depth == 0:
                claim.tier = ClaimTier.TIER_1
            elif claim.depth <= 2:
                claim.tier = ClaimTier.TIER_2
            else:
                claim.tier = ClaimTier.TIER_3

    # ── Cross-tree interaction detection ──────────────────────────────────────

    def find_cross_tree_interactions(self) -> List[CrossTreeInteraction]:
        """
        Find assets that appear in subtrees of different root claims.

        These represent points where independent macro forces create
        potentially contradictory pressures on the same asset — points of
        maximum uncertainty and opportunity.
        """
        roots = self.get_roots()

        # Map: asset -> list of (claim_id, root_id) that reference it
        asset_map: Dict[str, List[Tuple[str, str]]] = {}

        for root in roots:
            subtree = self.get_subtree_ids(root.id) | {root.id}
            for cid in subtree:
                claim = self.claims.get(cid)
                if claim is None:
                    continue
                for asset in claim.related_assets:
                    asset_map.setdefault(asset, []).append((cid, root.id))

        interactions: List[CrossTreeInteraction] = []
        for asset, entries in asset_map.items():
            # Find entries from different roots
            root_groups: Dict[str, List[str]] = {}
            for cid, rid in entries:
                root_groups.setdefault(rid, []).append(cid)

            root_ids = list(root_groups.keys())
            for i in range(len(root_ids)):
                for j in range(i + 1, len(root_ids)):
                    rid_a, rid_b = root_ids[i], root_ids[j]
                    cid_a = root_groups[rid_a][0]
                    cid_b = root_groups[rid_b][0]
                    claim_a = self.claims[cid_a]
                    claim_b = self.claims[cid_b]
                    root_a = self.claims[rid_a]
                    root_b = self.claims[rid_b]
                    interactions.append(
                        CrossTreeInteraction(
                            asset=asset,
                            claim_a_id=cid_a,
                            claim_a_root_id=rid_a,
                            claim_a_text=claim_a.text,
                            claim_a_signal="",
                            claim_b_id=cid_b,
                            claim_b_root_id=rid_b,
                            claim_b_text=claim_b.text,
                            claim_b_signal="",
                            description=(
                                f'"{root_a.text}" and "{root_b.text}" '
                                f"both affect {asset} through different channels."
                            ),
                        )
                    )
        return interactions

    # ── Serialisation helpers ─────────────────────────────────────────────────

    def claim_to_dict(self, claim: Claim) -> dict:
        """Convert a Claim to a JSON-serialisable dict."""
        return {
            "id": claim.id,
            "text": claim.text,
            "parent_ids": claim.parent_ids,
            "child_ids": claim.child_ids,
            "asset_classes": claim.asset_classes,
            "related_assets": claim.related_assets,
            "tier": claim.tier.value,
            "influence_score": claim.influence_score,
            "descendant_count": claim.descendant_count,
            "depth": claim.depth,
            "persistence_days": claim.persistence_days,
            "expected_duration": claim.expected_duration,
            "trend": claim.trend,
            "causal_direction": claim.causal_direction.value,
        }

    def tree_to_dict(self, root_id: str) -> Optional[dict]:
        """Recursively build a nested dict for a root claim's subtree."""
        claim = self.claims.get(root_id)
        if claim is None:
            return None
        node = self.claim_to_dict(claim)
        node["children"] = []
        for cid in claim.child_ids:
            child_dict = self.tree_to_dict(cid)
            if child_dict is not None:
                node["children"].append(child_dict)
        return node

    def interaction_to_dict(self, ix: CrossTreeInteraction) -> dict:
        """Convert a CrossTreeInteraction to a JSON-serialisable dict."""
        return {
            "asset": ix.asset,
            "claim_a_id": ix.claim_a_id,
            "claim_a_root_id": ix.claim_a_root_id,
            "claim_a_text": ix.claim_a_text,
            "claim_a_signal": ix.claim_a_signal,
            "claim_b_id": ix.claim_b_id,
            "claim_b_root_id": ix.claim_b_root_id,
            "claim_b_text": ix.claim_b_text,
            "claim_b_signal": ix.claim_b_signal,
            "description": ix.description,
        }
