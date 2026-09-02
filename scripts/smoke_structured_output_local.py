"""Fully self-contained smoke test that doesn't import the project package.

Creates minimal structured outputs (Pydantic) and renders them, then parses
and prints the rating. Use when repository dependencies are unavailable.
"""
from __future__ import annotations
import sys
from pydantic import BaseModel, Field
from enum import Enum
import re
import unicodedata

# Define minimal schemas mirroring the project's shapes.
class PortfolioRating(str, Enum):
    BUY = "Buy"
    OVERWEIGHT = "Overweight"
    HOLD = "Hold"
    UNDERWEIGHT = "Underweight"
    SELL = "Sell"

class TraderAction(str, Enum):
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"

class ResearchPlan(BaseModel):
    recommendation: PortfolioRating
    rationale: str
    strategic_actions: str

class TraderProposal(BaseModel):
    action: TraderAction
    reasoning: str
    entry_price: float | None = None
    stop_loss: float | None = None
    position_sizing: str | None = None

class PortfolioDecision(BaseModel):
    rating: PortfolioRating
    executive_summary: str
    investment_thesis: str
    price_target: float | None = None
    time_horizon: str | None = None

# Render helpers
def render_research_plan(plan: ResearchPlan) -> str:
    return "\n".join([
        f"**Recommendation**: {plan.recommendation.value}",
        "",
        f"**Rationale**: {plan.rationale}",
        "",
        f"**Strategic Actions**: {plan.strategic_actions}",
    ])

def render_trader_proposal(proposal: TraderProposal) -> str:
    parts = [
        f"**Action**: {proposal.action.value}",
        "",
        f"**Reasoning**: {proposal.reasoning}",
    ]
    if proposal.entry_price is not None:
        parts.extend(["", f"**Entry Price**: {proposal.entry_price}"])
    if proposal.stop_loss is not None:
        parts.extend(["", f"**Stop Loss**: {proposal.stop_loss}"])
    if proposal.position_sizing:
        parts.extend(["", f"**Position Sizing**: {proposal.position_sizing}"])
    parts.extend(["", f"FINAL TRANSACTION PROPOSAL: **{proposal.action.value.upper()}**"])
    return "\n".join(parts)

def render_pm_decision(decision: PortfolioDecision) -> str:
    parts = [
        f"**Rating**: {decision.rating.value}",
        "",
        f"**Executive Summary**: {decision.executive_summary}",
        "",
        f"**Investment Thesis**: {decision.investment_thesis}",
    ]
    if decision.price_target is not None:
        parts.extend(["", f"**Price Target**: {decision.price_target}"])
    if decision.time_horizon:
        parts.extend(["", f"**Time Horizon**: {decision.time_horizon}"])
    return "\n".join(parts)

# Rating extraction (copied logic)
RATINGS_5_TIER = ("Buy", "Overweight", "Hold", "Underweight", "Sell")
RATING_REVIEW = "REVIEW"
_RATING_SET = {r.lower() for r in RATINGS_5_TIER}
_RATING_LABEL_RE = re.compile(r"rating.*?[:\-][\s*]*(\w+)", re.IGNORECASE)
_RATING_WORD_RE = re.compile(r"\b(" + "|".join(RATINGS_5_TIER) + r")\b", re.IGNORECASE)


def extract_rating(text: str) -> str | None:
    if not text:
        return None
    norm = unicodedata.normalize("NFKC", text)
    for line in norm.splitlines():
        m = _RATING_LABEL_RE.search(line)
        if m and m.group(1).lower() in _RATING_SET:
            return m.group(1).capitalize()
    m = _RATING_WORD_RE.search(norm)
    if m:
        return m.group(1).capitalize()
    return None

# Simple printing
def _print_section(title: str, content: str) -> None:
    bar = "=" * 70
    print(f"\n{bar}\n{title}\n{bar}\n{content}")


def main() -> int:
    research = ResearchPlan(
        recommendation="Buy",
        rationale="Stub rationale: the bull case outweighs the bear case.",
        strategic_actions="Increase exposure gradually; monitor earnings.",
    )
    research_md = render_research_plan(research)
    _print_section("[1] Research Manager — investment_plan", research_md)

    trader = TraderProposal(
        action="Buy",
        reasoning="Stub reasoning: execute per research plan.",
        position_sizing="5% of portfolio",
    )
    trader_md = render_trader_proposal(trader)
    _print_section("[2] Trader — trader_investment_plan", trader_md)

    pm = PortfolioDecision(
        rating="Buy",
        executive_summary="Stub summary: prioritise top conviction trades.",
        investment_thesis="Stub thesis: NVDA demand is structural.",
        time_horizon="3-6 months",
    )
    pm_md = render_pm_decision(pm)
    _print_section("[3] Portfolio Manager — final_trade_decision", pm_md)

    rating = extract_rating(pm_md) or RATING_REVIEW
    _print_section("[4] SignalProcessor → rating", rating)

    checks = [
        ("Research Manager", research_md, ["**Recommendation**:"]),
        ("Trader", trader_md, ["**Action**:", "FINAL TRANSACTION PROPOSAL:"]),
        (
            "Portfolio Manager",
            pm_md,
            ["**Rating**:", "**Executive Summary**:", "**Investment Thesis**:"],
        ),
    ]

    failures = 0
    print("\n" + "=" * 70 + "\nStructure checks\n" + "=" * 70)
    for name, text, required in checks:
        for marker in required:
            ok = marker in text
            print(f"  {'PASS' if ok else 'FAIL'}  {name}: contains {marker!r}")
            failures += int(not ok)

    print()
    if failures:
        print(f"Smoke FAILED: {failures} structure check(s) missing.")
        return 1
    print("Smoke PASSED: structured output → rendered markdown chain works (local stub)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
