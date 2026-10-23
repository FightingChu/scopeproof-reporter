import tempfile
from pathlib import Path

from scopeproof.io import atomic_write_text

SCENARIO_ID = "S6"
NAME = "atomic local output"


def run(check):
    with tempfile.TemporaryDirectory() as folder:
        destination = Path(folder) / "reports" / "assessment.md"
        atomic_write_text(destination, "complete report\n")
        check.equal("complete report\n", destination.read_text(encoding="utf-8"), "output differs")
        check.equal([], list(destination.parent.glob("*.tmp")), "temporary files remain")
