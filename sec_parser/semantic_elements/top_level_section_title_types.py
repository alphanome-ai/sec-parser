from dataclasses import dataclass


@dataclass(frozen=True)
class TopLevelSectionIn10Q:
    identifier: str
    title: str
    order: int
    level: int = 0


InvalidTopLevelSectionIn10Q = TopLevelSectionIn10Q(
    identifier="invalid",
    title="Invalid",
    order=-1,
    level=1,
)

ALL_10Q_SECTIONS = (
    TopLevelSectionIn10Q(
        identifier="part1",
        title="Financial Information",
        order=0,
        level=0,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item1",
        title="Financial Statements",
        order=1,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item2",
        title="Management's Discussion and Analysis of Financial Condition and Results of Operations",
        order=2,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item3",
        title="Quantitative and Qualitative Disclosures About Market Risk",
        order=3,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part1item4",
        title="Controls and Procedures",
        order=4,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2",
        title="Other Information",
        order=5,
        level=0,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item1",
        title="Legal Proceedings",
        order=6,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item1a",
        title="Risk Factors",
        order=7,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item2",
        title="Unregistered Sales of Equity Securities and Use of Proceeds",
        order=8,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item3",
        title="Defaults Upon Senior Securities",
        order=9,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item4",
        title="Mine Safety Disclosures",
        order=10,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item5",
        title="Other Information",
        order=11,
        level=1,
    ),
    TopLevelSectionIn10Q(
        identifier="part2item6",
        title="Exhibits",
        order=12,
        level=1,
    ),
)

IDENTIFIER_TO_10Q_SECTION = {
    section.identifier: section for section in ALL_10Q_SECTIONS
}


TopLevelSectionType = TopLevelSectionIn10Q
