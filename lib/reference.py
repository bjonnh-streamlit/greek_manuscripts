from dataclasses import dataclass
from typing import Optional


# References for text
# we can refer to sections, subsections, lines or words
@dataclass(frozen=True, unsafe_hash=True)
class Reference:
    section: Optional[str]
    subsection: Optional[str] = None
    line: Optional[int] = None
    word: Optional[int] = None

    def nice_print(self):
        output = f"{self.section}"
        if self.subsection is not None and self.subsection.strip() != "":
            output += f" ({self.subsection}"
            if self.line:
                output += f".{self.line}"
                if self.word:
                    output += f".{self.word}"
            output += ")"
        return output

    def __str__(self):
        return self.nice_print()
