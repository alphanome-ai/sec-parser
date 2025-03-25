from dataclasses import dataclass


@dataclass(frozen=True)
class TopSectionInFiling:
    identifier: str
    title: str
    order: int
    level: int = 0


InvalidTopSectionInFiling = TopSectionInFiling(
    identifier="invalid",
    title="Invalid",
    order=-1,
    level=1,
)

@dataclass(frozen=True)
class FilingSections:
    all_sections: tuple[TopSectionInFiling, ...]
    identifier_to_section: dict[str, TopSectionInFiling]

    def __init__(self, all_sections: tuple[TopSectionInFiling, ...]) -> None:
        object.__setattr__(
            self,
            "identifier_to_section",
            {section.identifier: section for section in all_sections},
        )


FilingSectionsIn10Q = FilingSections(
    all_sections=(
        TopSectionInFiling(
            identifier="part1",
            title="Financial Information",
            order=0,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part1item1",
            title="Financial Statements",
            order=1,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item2",
            title="Management's Discussion and Analysis of Financial Condition and Results of Operations",
            order=2,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item3",
            title="Quantitative and Qualitative Disclosures About Market Risk",
            order=3,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item4",
            title="Controls and Procedures",
            order=4,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2",
            title="Other Information",
            order=5,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part2item1",
            title="Legal Proceedings",
            order=6,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item1a",
            title="Risk Factors",
            order=7,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item2",
            title="Unregistered Sales of Equity Securities and Use of Proceeds",
            order=8,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item3",
            title="Defaults Upon Senior Securities",
            order=9,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item4",
            title="Mine Safety Disclosures",
            order=10,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item5",
            title="Other Information",
            order=11,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item6",
            title="Exhibits",
            order=12,
            level=1,
        ),
    ),
)

FilingSectionsIn10K = FilingSections(
    all_sections=(
        TopSectionInFiling(
            identifier="part1",
            title="",
            order=0,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part1item1",
            title="Business",
            order=1,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item1a",
            title="Risk Factors",
            order=2,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item1b",
            title="Unresolved Staff Comments",
            order=3,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item1c",
            title="Cybersecurity",
            order=4,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item2",
            title="Properties",
            order=5,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item3",
            title="Legal Proceedings",
            order=6,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part1item4",
            title="Mine Safety Disclosures",
            order=7,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2",
            title="",
            order=8,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part2item5",
            title="Market",
            order=9,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item6",
            title="[Reserved]",
            order=10,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item7",
            title="Management's Discussion and Analysis of Financial Condition and Results of Operations",
            order=11,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item7a",
            title="Quantitative and Qualitative Disclosures about Market Risks",
            order=12,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item8",
            title="Financial Statements",
            order=13,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item9",
            title="Changes in and Disagreements With Accountants on Accounting and Financial Disclosure",
            order=14,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item9a",
            title="Controls and Procedures",
            order=15,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item9b",
            title="Other Information",
            order=16,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part2item9c",
            title="Disclosure Regarding Foreign Jurisdictions that Prevent Inspections",
            order=17,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part3",
            title="",
            order=18,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part3item10",
            title="Directors, Executive Officers and Corporate Governance",
            order=19,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part3item11",
            title="Executive Compensation",
            order=20,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part3item12",
            title="Security Ownership of Certain Beneficial Owners and Management and Related Stockholder Matters",
            order=21,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part3item13",
            title="Certain Relationships and Related Transactions, and Director Independence",
            order=22,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part3item14",
            title="Principal Accounting Fees and Services",
            order=23,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part4",
            title="",
            order=24,
            level=0,
        ),
        TopSectionInFiling(
            identifier="part4item15",
            title="Exhibits, Financial Statement Schedules Signatures",
            order=25,
            level=1,
        ),
        TopSectionInFiling(
            identifier="part4item16",
            title="Form 10-K Summary",
            order=26,
            level=1,
        ),
    ),
)
