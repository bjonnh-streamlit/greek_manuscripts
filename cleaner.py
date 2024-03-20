#!/usr/bin/env python3
# Cleanup docx files by removing headers, footers and comments
import os
from tempfile import mkstemp

from docx import Document

def remove_headers_footnotes_comments(docx_path, out_path):
    doc = Document(docx_path)
    counts = { "headers": 0, "footnotes": 0, "comments": 0, "sections": 0 }

    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape'
    }

    # Parse the XML
    tree = doc._element

    # Remove headers
    for elem in tree.findall('.//w:hdr', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["headers"] += 1
            parent.remove(elem)

    # Remove footnotes
    for elem in tree.findall('.//w:footnoteReference', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["footnotes"] += 1
            parent.remove(elem)
    for elem in tree.findall('.//w:footnotePr', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["footnotes"] += 1
            parent.remove(elem)

    # Remove comments
    for elem in tree.findall('.//w:commentRangeStart', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["comments"] += 1
            parent.remove(elem)
    for elem in tree.findall('.//w:commentRangeEnd', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["comments"] += 1
            parent.remove(elem)
    for elem in tree.findall('.//w:commentReference', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["comments"] += 1
            parent.remove(elem)
    for elem in tree.findall('.//w:comment', namespaces):
        parent = elem.getparent()
        if parent is not None:
            counts["comments"] += 1
            parent.remove(elem)


    tmp_file = mkstemp(suffix=".docx")
    doc.save(tmp_file[1])

    # We probably don't need that anymore but doing it anyway
    document = Document(tmp_file[1])
    for section in document.sections:
        counts["sections"] += 1
        section.different_first_page_header_footer = False
        section.header.is_linked_to_previous = True
        section.footer.is_linked_to_previous = True
        section.header.text = None
        section.footer.text = None
    document.save(out_path)

    os.remove(tmp_file[1])
    print(f"Headers, footnotes, and comments removed. Modified document saved as: {out_path}")
    print(f"Counts: {counts}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cleanup docx files by removing headers, footers and comments")
    parser.add_argument("docx_path", help="Path to the input docx file")
    parser.add_argument("out_path", help="Path to the output docx file")
    args = parser.parse_args()

    remove_headers_footnotes_comments(args.docx_path, args.out_path)
