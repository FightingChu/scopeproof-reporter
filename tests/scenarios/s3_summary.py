from scopeproof.report import build_markdown
from tests.support import finding, scope

SCENARIO_ID = "S3"
NAME = "finding summary"


def run(check):
    output = build_markdown(scope(), [finding()])
    check.contains("ASSESS-TEST-001", output, "assessment id is missing")
    check.contains("| Medium | 1 |", output, "medium finding count is wrong")
    check.contains("Total findings: **1**", output, "total finding count is wrong")
