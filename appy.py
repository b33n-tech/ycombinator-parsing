import streamlit as st
import pandas as pd
from io import BytesIO
import re

st.title("Y Combinator Startup List Parser - version flexible")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Name", "Location", "Pitch", "Incubation Period", "Segments/Fields"
    ])

st.write("""
Colle ici plusieurs startups à la suite.
Chaque startup commence par une ligne contenant le nom et la localisation (avec au moins 2 virgules).
Les autres lignes sont le pitch, incubation, segments et fields.
Le parsing est flexible pour gérer un nombre variable de lignes par startup.
""")

startup_text = st.text_area("Paste startup data here:", height=350)

def is_startup_header(line):
    # On considère qu'une ligne qui contient au moins 2 virgules est un header Name+Location
    return line.count(",") >= 2

def parse_startups_flexible(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip() != '']
    startups = []
    current_block = []

    for line in lines:
        if is_startup_header(line):
            # Nouveau bloc détecté
            if current_block:
                startups.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        startups.append(current_block)
    
    parsed_startups = []
    errors = []
    
    # Pattern simple pour date incubation type "Summer 2021", "Fall 2020" etc.
    date_pattern = re.compile(r'(Spring|Summer|Fall|Winter|Winter\s*\d{4}|\d{4})', re.IGNORECASE)

    for i, block in enumerate(startups):
        if len(block) < 2:
            errors.append(f"Startup #{i+1} : bloc trop court (moins de 2 lignes).")
            continue
        
        # Name + Location sur la 1ère ligne
        header = block[0]
        # Le nom est tout avant la 1ère virgule qui sépare le nom de la localisation (ici plus compliqué avec ton exemple où le nom et la ville sont collés)
        # Tentative de parsing : on cherche la 1ère virgule, le nom est ce qui est avant + peut être un trim
        # Comme le nom est collé au début, on va extraire le nom en cherchant la première virgule et prendre tout avant
        comma_pos = header.find(',')
        if comma_pos == -1:
            errors.append(f"Startup #{i+1} : ligne header invalide, pas de virgule détectée.")
            continue
        
        name = header[:comma_pos].strip()
        location = header[comma_pos+1:].strip()
        
        # Ensuite on analyse les autres lignes
        pitch = ""
        incubation = ""
        segments_fields = []
        
        # Recherche de la ligne incubation via regex
        incubation_idx = -1
        for idx, line in enumerate(block[1:], 1):
            if date_pattern.search(line):
                incubation = line
                incubation_idx = idx
                break
        
        if incubation_idx == -1:
            # Pas trouvé d'incubation : on suppose que la 2e ligne est pitch, le reste segments
            if len(block) > 1:
                pitch = block[1]
                segments_fields = block[2:]
            else:
                pitch = ""
                segments_fields = []
        else:
            # pitch = concat des lignes entre 1 et incubation_idx-1 (normalement 1 ligne)
            if incubation_idx > 1:
                pitch = " ".join(block[1:incubation_idx])
            else:
                pitch = block[1]
            # segments/fields = tout ce qui suit incubation_idx
            segments_fields = block[incubation_idx+1:]
        
        parsed_startups.append({
            "Name": name,
            "Location": location,
            "Pitch": pitch,
            "Incubation Period": incubation,
            "Segments/Fields": " | ".join(segments_fields)  # séparés par pipe pour lisibilité
        })
    
    return parsed_startups, errors

col1, col2 = st.columns(2)

with col1:
    if st.button("Ajouter les startups collées"):
        parsed_list, error_list = parse_startups_flexible(startup_text)
        if error_list:
            for err in error_list:
                st.error(err)
        if parsed_list:
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame(parsed_list)],
                ignore_index=True
            )
            st.success(f"{len(parsed_list)} startups ajoutées avec succès.")
            st.experimental_rerun()

with col2:
    if st.button("Télécharger XLSX"):
        if st.session_state.data.empty:
            st.warning("Pas de données à télécharger pour le moment.")
        else:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.data.to_excel(writer, index=False, sheet_name='Startups')
                writer.save()
            output.seek(0)
            st.download_button(
                label="Télécharger startups.xlsx",
                data=output,
                file_name="startups.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

st.write("---")
st.write("Startups actuellement dans la base :")
st.dataframe(st.session_state.data)
