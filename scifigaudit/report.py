import json

from .models import AuditResult


def report_json(result: AuditResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False)

