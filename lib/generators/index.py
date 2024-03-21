from itertools import groupby

from lib.decoder_state import DecoderState


def nice_printer_references(content):
    """Prints the sections only when it is a new one."""
    output = []
    for thing in groupby(content, lambda entry: entry.subsection):
        list_of_subref = [f"{ref.section}.{ref.line}" for ref in thing[1]]
        output += [f"{thing[0]} ({' ‖ '.join(list_of_subref)})"]
    return "; ".join(output) + "."


def word_info(word, source, raw=False):
    content = source[word]
    if raw:
        return {"count": len(content), "references": content}
    else:
        return f"({len(content)}) − {nice_printer_references(content)}"


def index(decoder_state: DecoderState, reverse=False, raw=False):
    if reverse:
        source = decoder_state.reversed_word_occurrences
    else:
        source = decoder_state.word_occurrences

    for word in sorted(source.keys(), key=decoder_state.pyuca_collator.sort_key):
        yield word, word_info(word, source, raw)
