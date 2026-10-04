def draft_flagged_category(
    category: str,
    prev_month: str,
    month: str,
    previous_revenue: float,
    current_revenue: float,
    mom_pct: float,
) -> str:
    """Fill the prompt-pack structure using verified inputs only.

    This is deterministic and offline: it never calls an AI service.
    """
    if mom_pct > 0:
        movement = "increased"
    elif mom_pct < 0:
        movement = "decreased"
    else:
        movement = "did not change"

    return (
        f"Context: {category} revenue in {month} vs. {prev_month}. "
        f"Insight — FACT: Revenue {movement} from "
        f"INR {previous_revenue:.2f} to INR {current_revenue:.2f}; "
        f"month-on-month change was {mom_pct}% (flagged). "
        f"Implication — RECOMMENDATION: Ask the category manager to "
        f"compare order counts and reseller concentration for "
        f"{category} across {prev_month} and {month}. "
        f"HYPOTHESIS: Changes in volume or reseller activity could "
        f"contribute, but this revenue comparison does not prove a cause. "
        f"Draft held for human approval."
    )
