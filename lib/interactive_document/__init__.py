from itertools import groupby

from jinja2 import Environment, FileSystemLoader

from lib.decoder_state import DecoderState
from lib.generators.index import index



class InteractiveDocument:
    def __init__(self):
        self.html = ""
        self.jinja_env = Environment(loader=FileSystemLoader("html_templates"))
        self.jinja_template = self.jinja_env.get_template("interactive_document.html")
        self.css = self.jinja_env.get_template("output.css")

    def from_decoder_state(self, state: DecoderState) -> "InteractiveDocument":
        content = ""
        content += "<h2 id=\"text\">Text</h2>\n"
        content += "<div class=\"text\">\n"
        for reference in state.full_text_word_linked.keys():
            current_block = state.full_text_word_linked[reference]
            content += f"<h3 id=\"sec_{reference.section}_{reference.subsection}\">{reference.nice_print()}</h3>\n"
            for word in current_block:
                content += f"<a href=\"#w_{word[1]}\">{word[0]} </a>"
        content += "</div>\n"

        content += "<h2 id=\"index\">Index</h2>\n"
        content += "<div class=\"index\">\n"
        for word, word_info in index(state, raw=True):
            content += f"\n<h3 id=\"w_{word}\">{word}</h3>\n"
            content += f"<p>{word_info['count']} occurrences<br>"
            for thing in groupby(word_info["references"], lambda entry: entry.subsection):
                list_of_subref = [f"<a onclick=\"highlightLinks('#w_{word}')\" href=\"#sec_{ref.section}_{ref.subsection}\">{ref.section}.{ref.line}</a>" for ref in thing[1]]
                content += "; ".join([f"{thing[0]} ({' ‖ '.join(list_of_subref)})"]) + " - "
            content += "</p>"
        content += "</div>\n"

        lang = "grc"
        title = state.title

        html = self.jinja_template.render(
            {
                "lang": lang,
                "title": title,
                "content": content,
                "css": self.css.render(),
                "sidebar": [
                    {"title": "Text", "link": "#text"},
                    {"title": "Index", "link": "#index"},
                ]
            }
        )
        doc = InteractiveDocument()
        doc.html = html
        return doc
