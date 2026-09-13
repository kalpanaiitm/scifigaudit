from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Check:
    key: str
    label: str
    status: str
    message: str
    evidence: str
    weight: int


@dataclass(frozen=True)
class AuditResult:
    score: int
    checks: list[Check]
    human_review: list[str]
    scope_notice: str

    def to_dict(self) -> dict:
        return asdict(self)

