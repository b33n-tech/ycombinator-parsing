import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="📄 Scraper intelligent (Ctrl+A toléré)", layout="wide")
st.title("📄 Scraper intelligent (avec champs multilignes)")

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
    blocks = re.split(r"\n(?=\w.+\nFOUNDERS\n)", text)
    return [block.strip() for block in blocks if "FOUNDERS" in block]

def extract_section_between(label, next_labels, block):
    # Cherche les lignes après un label jusqu'à l’un des prochains labels
    lines = block.splitlines()
    content = []
    capture = False
    for line in lines:
        if line.strip().upper() == label:
            capture = True
            continue
        if capture:
            if line.strip().upper() in next_labels:
                break
            content.append(line.strip())
    return ", ".join([l for l in content if l])

def extract_about(text):
    match = re.search(r"About\n(.*)", text, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_data(block):
    lines = block.strip().splitlines()
    name = lines[0].strip()
    pitch = next((line.strip() for line in lines[1:] if line.strip() and line.strip().upper() not in {
        "FOUNDERS", "YEAR FOUNDED", "CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"
    }), "")

    # Champs multilignes
    return {
        "Name": name,
        "Pitch": pitch,
        "Founders": extract_section_between("FOUNDERS", {"YEAR FOUNDED", "CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"}, block),
        "Year": extract_section_between("YEAR FOUNDED", {"CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"}, block),
        "Categories": extract_section_between("CATEGORY", {"TEAM SIZE", "WEBSITE", "ABOUT"}, block),
        "Team Size": extract_section_between("TEAM SIZE", {"WEBSITE", "ABOUT"}, block),
        "Website": extract_section_between("WEBSITE", {"ABOUT"}, block),
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
