import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Y Combinator Startup List Parser")

if 'data' not in st.session_state:
    # DataFrame to hold all startups
    st.session_state.data = pd.DataFrame(columns=[
        "Name", "Location", "Pitch", "Incubation Period", "Segment", "Field"
    ])

st.write("Paste one startup entry exactly like this format (5 lines):")
st.write("""
