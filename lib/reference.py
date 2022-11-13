from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, unsafe_hash=True)
class Reference:
    section: Optional[str]
    subsection: Optional[str]
    line: Optional[int]

    def nice_print(self):
        return f"{self.subsection} ({self.section}.{self.line})"

    def __str__(self):
        return self.nice_print()
