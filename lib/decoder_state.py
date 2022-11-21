### We store the decoder state as its own object so we can serialize it
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set

from lib.reference import Reference


@dataclass(frozen=True, unsafe_hash=True)
class DecoderState:
    short_references: List[Reference] = field(default_factory=lambda: [])
    sections: Set[str] = field(default_factory=lambda: set())
    subsections: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))
    full_text: Dict[Reference, List[str]] = field(default_factory=lambda: defaultdict(list))