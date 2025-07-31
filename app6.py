import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="📄 Scraper de Fiches Projets", layout="wide")
st.title("📄 Scraper multi-fiches depuis texte brut (copier-coller complet)")

if "projects" not in st.session_state:
    st.session_state.projects = []

def clean_text(text):
    return re.sub(r"[^\x00-\x7F]+", " ", text).strip()

def extract_project_blocks(text):
    # Découper le texte en "blocs projets" à partir de lignes contenant 'FOUNDERS'
    blocks = re.split(r"\n(?=.+\nFOUNDERS\n)", text)
    return [block.strip() for block in blocks if "FOUNDERS" in block]

def extract_data(block):
    lines = block.strip().splitlines()
    name, pitch = lines[0], ""
    
    # Trouver la première ligne non vide après le nom (le pitch)
    for line in lines[1:]:
        if line.strip() and not line.strip().upper() in ["FOUNDERS", "YEAR FOUNDED", "CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"]:
            pitch = line.strip()
            break

    def extract_field(label):
        match = re.search(rf"{label}\n(.*?)\n", block, re.DOTALL)
        if match:
            return match.group(1).replace("\n", ", ").strip()
        return ""

    def extract_about(text):
        match = re.search(r"About\n(.*)", text, re.DOTALL)
        return match.group(1).strip() if match else ""

    return {
        "Name": name.strip(),
        "Pitch": pitch,
        "Founders": extract_field("FOUNDERS"),
        "Year": extract_field("YEAR FOUNDED"),
        "Categories": extract_field("CATEGORY"),
        "Team Size": extract_field("TEAM SIZE"),
        "Website": extract_field("WEBSITE"),
        "Description": extract_about(block)
    }

# Interface
with st.form("multi_add_form"):
    raw_text = st.text_area("Copiez-collez ici un gros bloc avec plusieurs fiches (Ctrl+A possible)", height=600)
    multi_submit = st.form_submit_button("Analyser les fiches")

if multi_submit and raw_text:
    raw_text = clean_text(raw_text)
    blocks = extract_project_blocks(raw_text)
    st.info(f"{len(blocks)} fiche(s) détectée(s).")

    for block in blocks:
        data = extract_data(block)
        st.session_state.projects.append(data)
    st.success("Toutes les fiches valides ont été ajoutées.")

# Affichage final
if st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    st.subheader("📊 Projets extraits")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger le CSV", csv, "projets.csv", "text/csv")
