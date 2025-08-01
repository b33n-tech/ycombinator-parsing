import streamlit as st
import re
import pandas as pd
from io import BytesIO

st.title("Parser startup avec séparation par ligne vide avant chaque startup")

input_text = st.text_area("Colle ici ton contenu startup brut", height=400)

def insert_empty_line_before_startup_name(text):
    lines = text.splitlines()
    round_pattern = re.compile(r"^(Seed Round|Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)( in \d{4})?$")
    
    # Trouver index des lignes noms startup (juste avant ligne tour)
    name_indexes = []
    for i, line in enumerate(lines):
        if round_pattern.match(line):
            name_idx = i - 1
            if name_idx >= 0:
                name_indexes.append(name_idx)

    # Insérer ligne vide avant chaque nom startup sauf le premier
    for idx in reversed(name_indexes[1:]):
        lines.insert(idx, "")

    return "\n".join(lines)

def parse_startups(text):
    # Split sur lignes vides (blanches) pour isoler chaque startup
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    startups = []
    round_pattern = re.compile(r"^(Seed Round|Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)( in \d{4})?$")
    
    for block in blocks:
        lines = block.splitlines()
        # On doit avoir au moins 2 lignes : nom startup + tour de levée + pitch (au moins 1 ligne)
        if len(lines) < 3:
            continue
        name = lines[0].strip()
        round_line = lines[1].strip()
        pitch = " ".join(line.strip() for line in lines[2:])
        
        # Vérifier que la 2e ligne correspond bien au tour
        if not round_pattern.match(round_line):
            # Si non, on essaie d'inverser nom et tour (au cas où)
            if round_pattern.match(name):
                # Inverser
                name, round_line = round_line, name
            else:
                # Ligne tour non détectée => on skip ce block
                continue
        
        startups.append({
            "Startup": name,
            "Tour de levée": round_line,
            "Pitch": pitch
        })
    return startups

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Startups')
    return output.getvalue()

if input_text:
    processed_text = insert_empty_line_before_startup_name(input_text)
    startups = parse_startups(processed_text)

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
        st.warning("Aucune startup détectée. Vérifie le format du texte collé.")
