"""ScopeProof Reporter public API."""

from .catalog import RuleCatalog
from .models import Evidence, Finding, Rule, ScopeManifest, ValidationError
from .profiles import AssessmentProfile, ProfileCatalog
from .report import build_markdown
from .service import compile_report, validate_inputs

__all__ = [
    "Evidence",
    "Finding",
    "Rule",
    "RuleCatalog",
    "AssessmentProfile",
    "ProfileCatalog",
    "ScopeManifest",
    "ValidationError",
    "build_markdown",
    "compile_report",
    "validate_inputs",
]
__version__ = "0.1.0"
