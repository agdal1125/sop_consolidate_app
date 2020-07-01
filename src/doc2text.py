import os
import json
from docx import Document
from io import StringIO, BytesIO

def para_to_text(p):
    """
    A function to find every texts in the paragraph

    params
    ----
    p : docx.Document.Paragraph object

    returns
    ----
    str 

    """
    rs = p._element.xpath(".//w:t")
    return "".join([r.text for r in rs])


def sop_to_text(file_path):
    """
    Converts SOP.docx into plain text

    params
    ----
    file_path : str (path to the SOP document) 

    returns
    ----
    str
    """
    text = []
    with open(file_path, 'rb') as f:
        source_stream = BytesIO(f.read())
    f.close()

    doc = Document(source_stream)
    paras = doc.paragraphs
    for p in paras:
        text.append(para_to_text(p))
            
    text = " ".join(text).strip()
    return text