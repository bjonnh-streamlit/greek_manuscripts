from dataclasses import dataclass


@dataclass(frozen=True, unsafe_hash=True)
class Reference:
    section: str | None
    subsection: str | None
    line: int | None

    def nice_print(self):
        return f"{self.subsection} ({self.section}.{self.line})"

    def __str__(self):
        return self.nice_print()
