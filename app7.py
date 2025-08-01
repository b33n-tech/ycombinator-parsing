import streamlit as st
import re
import pandas as pd
from io import BytesIO

st.title("Parser de contenu startup")

input_text = st.text_area("Colle ici ton contenu (Nom startup / Tour / Pitch)", height=300)

def parse_startups(text):
    pattern = re.compile(
        r"(?P<name>^[A-Z][^\n]+)\n"
        r"(?P<round>(Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)[^\n]*)\n"
        r"(?P<pitch>.*?)(?=\n[A-Z][^\n]+\n(?:Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)|\Z)",
        re.MULTILINE | re.DOTALL
    )

    results = []
    for match in pattern.finditer(text):
        name = match.group("name").strip()
        round_ = match.group("round").strip()
        pitch = match.group("pitch").strip().replace('\n', ' ')
        results.append({"Startup": name, "Tour de levée": round_, "Pitch": pitch})

    return results

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Startups')
        writer.save()
    processed_data = output.getvalue()
    return processed_data

if input_text:
    startups = parse_startups(input_text)
    if startups:
        df = pd.DataFrame(startups)
        st.dataframe(df)

        # Générer le fichier Excel
        excel_data = to_excel(df)

        st.download_button(
            label="Télécharger en Excel (.xlsx)",
            data=excel_data,
            file_name="startups.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Aucun startup détecté dans le texte collé. Vérifie le format.")
