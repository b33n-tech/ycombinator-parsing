import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Y Combinator Startup List Parser")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Name", "Location", "Pitch", "Incubation Period", "Segment", "Field"
    ])

st.write("Format attendu pour chaque entrée (5 lignes) :")
st.write("Name, Location")
st.write("Pitch")
st.write("Incubation Period")
st.write("Segment")
st.write("Field")

startup_text = st.text_area("Paste startup info here (5 lines):", height=150)

def parse_startup(text):
    lines = [line.strip() for line in text.strip().split('\n')]
    if len(lines) != 5:
        return None, "Error: The input should have exactly 5 lines."
    first_line = lines[0]
    if ',' not in first_line:
        return None, "Error: First line must contain startup name and location separated by a comma."
    name, location = first_line.split(',', 1)
    name = name.strip()
    location = location.strip()
    pitch = lines[1]
    incubation = lines[2]
    segment = lines[3]
    field = lines[4]
    return {
        "Name": name,
        "Location": location,
        "Pitch": pitch,
        "Incubation Period": incubation,
        "Segment": segment,
        "Field": field
    }, None

col1, col2 = st.columns(2)

with col1:
    if st.button("Add startup entry (Next copy)"):
        parsed, error = parse_startup(startup_text)
        if error:
            st.error(error)
        else:
            st.session_state.data = st.session_state.data.append(parsed, ignore_index=True)
            st.success(f"Added startup: {parsed['Name']}")
            st.experimental_rerun()

with col2:
    if st.button("Download XLSX"):
        if st.session_state.data.empty:
            st.warning("No data to download yet.")
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.data.to_excel(writer, index=False, sheet_name='Startups')
                writer.save()
            output.seek(0)
            st.download_button(
                label="Download startups.xlsx",
                data=output,
                file_name="startups.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.write("---")
st.dataframe(st.session_state.data)
