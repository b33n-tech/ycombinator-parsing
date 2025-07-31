import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="📄 Scraper de Fiches Projets", layout="wide")
st.title("📄 Scraper intelligent (Ctrl+A toléré)")

if "projects" not in st.session_state:
    st.session_state.projects = []

def clean_text(text):
    # Garde seulement la portion utile entre les blocs "All portfolio" et "Media"
    start_match = re.search(r"All portfolio", text)
    end_match = re.search(r"Media\s+Want to join our portfolio\?", text)
    if start_match and end_match:
        text = text[start_match.end():end_match.start()]
    return re.sub(r"[^\x00-\x7F]+", " ", text).strip()

def extract_project_blocks(text):
    # Découper en projets à partir de "FOUNDERS" détecté au milieu d’un bloc cohérent
    blocks = re.split(r"\n(?=\w.+\nFOUNDERS\n)", text)
    return [block.strip() for block in blocks if "FOUNDERS" in block]

def extract_data(block):
    lines = block.strip().splitlines()
    name, pitch = lines[0], ""

    for line in lines[1:]:
        if line.strip() and line.upper() not in [
            "FOUNDERS", "YEAR FOUNDED", "CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"
        ]:
            pitch = line.strip()
            break

    def extract_field(label):
        match = re.search(rf"{label}\n(.*?)\n", block, re.DOTALL)
        if match:
            return match.group(1).replace("\n", ", ").strip()
        return ""

    def extract_about(text):
        match = re.search(r"About\n(.*)", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

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

with st.form("multi_add_form"):
    raw_text = st.text_area("Copiez-collez ici le texte (Ctrl+A depuis Founders Inc., etc.)", height=600)
    multi_submit = st.form_submit_button("Analyser les fiches")

if multi_submit and raw_text:
    filtered_text = clean_text(raw_text)
    blocks = extract_project_blocks(filtered_text)
    st.info(f"{len(blocks)} fiche(s) détectée(s).")

    for block in blocks:
        data = extract_data(block)
        st.session_state.projects.append(data)
    st.success("Toutes les fiches valides ont été ajoutées.")

if st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    st.subheader("📊 Projets extraits")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger le CSV", csv, "projets.csv", "text/csv")
