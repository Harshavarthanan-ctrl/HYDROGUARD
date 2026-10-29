"""
Greater Chennai Corporation zone names.

Zone numbers follow the official GCC administrative zones.
"""

ZONE_NAMES = {
    "1": "Thiruvottiyur",
    "2": "Manali",
    "3": "Madhavaram",
    "4": "Tondiarpet",
    "5": "Royapuram",
    "6": "Thiru-Vi-Ka Nagar",
    "7": "Ambattur",
    "8": "Anna Nagar",
    "9": "Teynampet",
    "10": "Kodambakkam",
    "11": "Valasaravakkam",
    "12": "Alandur",
    "13": "Adyar",
    "14": "Perungudi",
    "15": "Sholinganallur",
}


def get_zone_name(zone: str | None) -> str | None:
    """Return the human-readable GCC zone name."""
    if zone is None:
        return None

    return ZONE_NAMES.get(str(zone).strip())