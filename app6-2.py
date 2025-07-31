import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="📄 Scraper intelligent (Ctrl+A toléré)", layout="wide")
st.title("📄 Scraper intelligent (avec nettoyage manuel du texte)")

if "projects" not in st.session_state:
    st.session_state.projects = []

if "raw_text" not in st.session_state:
    st.session_state.raw_text = ""

def clean_text(raw):
    # Supprime tout avant "All portfolio"
    match = re.search(r"All portfolio", raw)
    if match:
        cleaned = raw[match.start():]
        return cleaned
    return raw

def clean_full_text(raw):
    # Supprime avant "All portfolio" ET après "Media\nWant to join our portfolio?"
    start_match = re.search(r"All portfolio", raw)
    end_match = re.search(r"Media\s+Want to join our portfolio\?", raw)
    if start_match and end_match:
        return raw[start_match.end():end_match.start()]
    elif start_match:
        return raw[start_match.end():]
    return raw

def extract_project_blocks(text):
    blocks = re.split(r"\n(?=\w.+\nFOUNDERS\n)", text)
    return [block.strip() for block in blocks if "FOUNDERS" in block]

def extract_section_between(label, next_labels, block):
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
    if match:
        return match.group(1).strip()
    return ""

def extract_data(block):
    lines = block.strip().splitlines()
    name = lines[0].strip()
    pitch = next((line.strip() for line in lines[1:] if line.strip() and line.strip().upper() not in {
        "FOUNDERS", "YEAR FOUNDED", "CATEGORY", "TEAM SIZE", "WEBSITE", "ABOUT"
    }), "")

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

with st.form("input_form"):
    text_input = st.text_area("Collez ici votre texte (Ctrl+A possible)", height=600, value=st.session_state.raw_text)
    clean_button = st.form_submit_button("Nettoyer le texte en supprimant l'en-tête inutile")
    parse_button = st.form_submit_button("Analyser les fiches")

if clean_button:
    st.session_state.raw_text = clean_text(text_input)
    st.success("Texte nettoyé : tout ce qui est avant 'All portfolio' a été supprimé.")

if parse_button:
    st.session_state.raw_text = text_input  # On sauvegarde le texte tel quel avant parsing
    filtered_text = clean_full_text(st.session_state.raw_text)
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
