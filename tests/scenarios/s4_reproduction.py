from scopeproof.report import build_markdown
from tests.support import finding, scope

SCENARIO_ID = "S4"
NAME = "reproduction steps"


def run(check):
    first = "curl -i http://127.0.0.1:18080/login -H 'Authorization: Bearer [REDACTED]'"
    second = "Compare the two synthetic responses."
    output = build_markdown(scope(), [finding()])
    check.contains("```text", output, "reproduction must use a fenced text block")
    check.contains(first, output, "first reproduction step is missing or not redacted")
    check.contains(second, output, "second reproduction step is missing")
    check.before(first, second, output, "reproduction order changed")

    empty = build_markdown(scope(), [finding(reproduction=())])
    check.contains("### Reproduction\n\nNot provided", empty, "empty steps need an explicit marker")
