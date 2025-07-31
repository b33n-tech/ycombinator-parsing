import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Y Combinator URL Parser")

st.write("Paste one or multiple Y Combinator company URLs (one per line).")

urls_text = st.text_area("Paste URLs here:", height=200)

def parse_urls(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    rows = []
    for url in lines:
        if url.endswith('/'):
            url = url[:-1]
        name = url.split('/')[-1]
        rows.append({"Name": name, "URL": url})
    return rows

if st.button("Parse URLs"):
    if not urls_text.strip():
        st.warning("Please paste some URLs first.")
    else:
        parsed = parse_urls(urls_text)
        df = pd.DataFrame(parsed)
        st.dataframe(df)

        # Prepare XLSX download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Companies')
        output.seek(0)
        st.download_button(
            label="Download XLSX",
            data=output,
            file_name="ycombinator_companies.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
