def alias_for(reseller_id: str) -> str:
    """Turn a reseller ID into its required coded alias."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(
    text: str, reseller_names: list[str]
) -> bool:
    """Return False if any supplied raw reseller name appears verbatim."""
    return not any(
        name in text for name in reseller_names if name
    )
