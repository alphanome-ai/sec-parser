from dataclasses import dataclass


@dataclass(frozen=True)
class TopLevelSectionIn10Q:
    identifier: str
    title: str
    level: int = 0


ALL_10Q_SECTIONS = (
    TopLevelSectionIn10Q(identifier="part1", title="Part I", level=0),
    TopLevelSectionIn10Q(
        identifier="part1item1",
        title="Financial Statements",
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item2",
        title="Management's Discussion and Analysis of Financial Condition and Results of Operations",
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item3",
        title="Quantitative and Qualitative Disclosures About Market Risk",
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item4",
        title="Controls and Procedures",
        level=1,
    ),
    TopLevelSectionIn10Q(identifier="part2", title="Part II", level=0),
    TopLevelSectionIn10Q(identifier="part2item1", title="Legal Proceedings", level=1),
    TopLevelSectionIn10Q(identifier="part2item1a", title="Risk Factors", level=1),
    TopLevelSectionIn10Q(
        identifier="part2item2",
        title="Unregistered Sales of Equity Securities and Use of Proceeds",
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item3",
        title="Defaults Upon Senior Securities",
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item4",
        title="Mine Safety Disclosures",
        level=1,
    ),
    TopLevelSectionIn10Q(identifier="part2item5", title="Other Information", level=1),
    TopLevelSectionIn10Q(identifier="part2item6", title="Exhibits", level=1),
)

IDENTIFIER_TO_10Q_SECTION = {
    section.identifier: section for section in ALL_10Q_SECTIONS
}


TopLevelSectionType = TopLevelSectionIn10Q
