import csv


def mom_growth(previous: float, current: float) -> float:
    """Return month-on-month revenue growth as a percentage."""
    if previous == 0:
        raise ValueError("Previous revenue is zero; MoM growth is undefined")

    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """Classify growth, including an exact-boundary case for human review."""
    if abs(mom_pct) > threshold:
        return "flagged"

    if abs(mom_pct) < threshold:
        return "not_flagged"

    return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
    """Check the category and revenue fields in a monthly revenue CSV."""
    errors = []

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # start=2 because line 1 contains the column headings.
        for line_number, row in enumerate(reader, start=2):
            month = (row.get("month") or "").strip()
            category = (row.get("category") or "").strip()
            revenue_text = (row.get("revenue") or "").strip()

            if not category:
                errors.append(
                    f"line {line_number}: missing category (month={month})"
                )

            if not revenue_text:
                errors.append(
                    f"line {line_number}: missing revenue "
                    f"(category={category})"
                )
                continue

            try:
                revenue = float(revenue_text)
            except ValueError:
                errors.append(
                    f"line {line_number}: revenue not numeric: "
                    f"{revenue_text!r}"
                )
                continue

            if revenue < 0:
                errors.append(
                    f"line {line_number}: negative revenue ({revenue}) "
                    f"for category={category}"
                )

    return (len(errors) == 0, errors)
