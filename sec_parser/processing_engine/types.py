from dataclasses import dataclass


@dataclass(frozen=True)
class ParsingOptions:
    # Integrity checks are disabled by default to improve performance
    html_integrity_checks: bool = False
