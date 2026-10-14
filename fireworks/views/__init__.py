"""View modules for the two strictly separated audiences."""

from __future__ import annotations

from typing import Any


def flatten(sections: list[dict[str, Any]]) -> list[str]:
    """Flatten structured view content into a list of human-visible strings.

    Used by the test suite to assert that the customer view never contains
    internal-only terms (see ``fireworks.assumptions.INTERNAL_ONLY_TERMS``).
    """
    texts: list[str] = []
    for s in sections:
        texts.append(s.get("heading", ""))
        if s.get("subheading"):
            texts.append(s["subheading"])
        for k in s.get("kpis", []):
            texts.append(k.get("label", ""))
            if k.get("help"):
                texts.append(k["help"])
        texts.extend(s.get("blocks", []))
    return texts
