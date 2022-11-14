import streamlit as st
import base64
from pathlib import Path

from last_changes import last_changes

VERSION="0.01"

def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded
def img_to_html(img_path):
    img_html = "<img src='data:image/png;base64,{}' class='img'>".format(
      img_to_bytes(img_path)
    )
    return img_html

st.set_page_config(
    page_title="Pyzantine",
    page_icon="👋",
)

st.write(f"# Welcome to the Pyzantine v{VERSION}")

st.sidebar.success("Select a tool above.")

st.markdown(
    f"""
    ## Pyzantine is a Python-based NLP tool for ancient medical greek texts.
    
    {img_to_html("logo/late_flag.png")}
    
    Currently, it is made to handle docx files formatted in a really special way.
    
    It allows to generate an index and a reversed-index and to analyze words in their contexts (WIP).  
        
    ### Last changes
""", unsafe_allow_html=True)

for version in last_changes:
    st.write(f"#### {version}")
    for change in last_changes[version]:
        st.write(change)
