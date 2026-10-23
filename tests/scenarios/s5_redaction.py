from scopeproof.report import build_markdown
from tests.support import finding, scope

SCENARIO_ID = "S5"
NAME = "secret redaction"


def run(check):
    output = build_markdown(scope(), [finding()])
    check.not_contains("SAMPLE-TOKEN-12345", output, "bearer token leaked")
    check.not_contains("SESSION-12345", output, "cookie value leaked")
    check.contains("[REDACTED]", output, "redaction marker is missing")
