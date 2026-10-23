from scopeproof.models import ValidationError
from scopeproof.scope import require_authorized_asset
from tests.support import scope

SCENARIO_ID = "S2"
NAME = "scope enforcement"


def run(check):
    try:
        require_authorized_asset(scope(), "outside.example.test")
    except ValidationError as exc:
        check.contains("not listed in scope", str(exc), "unexpected scope error")
    else:
        check.fail("out-of-scope evidence was accepted")
