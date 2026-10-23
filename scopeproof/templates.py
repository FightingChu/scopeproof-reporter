"""Read-only access to downstream report section templates."""

from pathlib import Path

from .models import ValidationError


class TemplateLibrary:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def names(self) -> tuple[str, ...]:
        return tuple(path.stem for path in sorted(self.root.glob("*.md")))

    def read(self, name: str) -> str:
        if not name.replace("-", "").replace("_", "").isalnum():
            raise ValidationError("template name contains unsupported characters")
        path = (self.root / f"{name}.md").resolve()
        if path.parent != self.root or not path.is_file():
            raise ValidationError(f"unknown template: {name}")
        return path.read_text(encoding="utf-8")
