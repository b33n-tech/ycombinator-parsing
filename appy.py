import streamlit as st
import pandas as pd
from io import BytesIO

st.title("Y Combinator Startup List Parser")

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Name", "Location", "Pitch", "Incubation Period", "Segment", "Field"
    ])

st.write("Tu peux coller plusieurs startups d'affilée, chaque startup doit faire 5 lignes, sans ligne vide entre.")

st.write("Format de chaque startup (5 lignes) :")
st.write("Name, Location")
st.write("Pitch")
st.write("Incubation Period")
st.write("Segment")
st.write("Field")

startup_text = st.text_area("Paste startup info here (multiple of 5 lines):", height=300)

def parse_startup(text_lines):
    """
    Parse 5 lines representing a startup entry.
    Return dict or (None, error message) if invalid.
    """
    if len(text_lines) != 5:
        return None, f"Erreur: Une entrée doit contenir exactement 5 lignes, ici {len(text_lines)} lignes."
    
    first_line = text_lines[0]
    if ',' not in first_line:
        return None, "Erreur: La première ligne doit contenir le nom et la localisation séparés par une virgule."
    
    name, location = first_line.split(',', 1)
    name = name.strip()
    location = location.strip()
    pitch = text_lines[1].strip()
    incubation = text_lines[2].strip()
    segment = text_lines[3].strip()
    field = text_lines[4].strip()
    
    return {
        "Name": name,
        "Location": location,
        "Pitch": pitch,
        "Incubation Period": incubation,
        "Segment": segment,
        "Field": field
    }, None

def parse_multiple_startups(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip() != '']
    results = []
    errors = []
    
    if len(lines) % 5 != 0:
        errors.append(f"Le nombre total de lignes ({len(lines)}) n'est pas un multiple de 5.")
        # On peut choisir de continuer avec la partie complète seulement, ou stopper
        # Ici je choisis de stopper
        return [], errors
    
    for i in range(0, len(lines), 5):
        block = lines[i:i+5]
        parsed, error = parse_startup(block)
        if error:
            errors.append(f"Erreur à l'entrée commençant à la ligne {i+1}: {error}")
        else:
            results.append(parsed)
    return results, errors

col1, col2 = st.columns(2)

with col1:
    if st.button("Ajouter les startups collées"):
        parsed_list, error_list = parse_multiple_startups(startup_text)
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
