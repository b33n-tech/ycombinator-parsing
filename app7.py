import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Parser startup avec ligne vide entre chaque bloc")

input_text = st.text_area("Colle ici ton contenu avec une ligne vide entre chaque startup", height=400)

def parse_startups_with_empty_lines(text):
    blocks = text.strip().split('\n\n')  # Split par double saut de ligne
    startups = []
    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) >= 3:
            name = lines[0]
            round_ = lines[1]
            pitch = ' '.join(lines[2:])
            startups.append({
                "Startup": name,
                "Tour de levée": round_,
                "Pitch": pitch
            })
    return startups

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Startups')
    return output.getvalue()

if input_text:
    startups = parse_startups_with_empty_lines(input_text)
    if startups:
        df = pd.DataFrame(startups)
        st.dataframe(df)

        excel_data = to_excel(df)
        st.download_button(
            label="Télécharger en Excel (.xlsx)",
            data=excel_data,
            file_name="startups.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Aucun startup détecté. Vérifie le format (3 lignes minimum par bloc).")
