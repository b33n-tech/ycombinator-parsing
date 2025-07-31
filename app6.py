import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="📄 Scraper Fiches Projets", layout="wide")

st.title("📄 Scraper de Fiches Projets")

# Initialisation
if "projects" not in st.session_state:
    st.session_state.projects = []

# Formulaire pour ajouter une fiche projet
with st.form("add_project_form"):
    fiche = st.text_area("Copiez-collez ici la fiche projet complète :", height=400)
    submitted = st.form_submit_button("Ajouter cette fiche")

if submitted and fiche:
    # Extraction des données via regex
    def extract_data(text):
        data = {}
        lines = text.splitlines()
        data["Name"] = lines[0].strip()
        data["Pitch"] = lines[1].strip() if len(lines) > 1 else ""

        data["Founders"] = re.search(r"FOUNDERS\s*(.*?)\s*(YEAR|CATEGORY|TEAM|WEBSITE)", text, re.DOTALL)
        data["Year"] = re.search(r"YEAR FOUNDED\s*(\d{4})", text)
        data["Categories"] = re.search(r"CATEGORY\s*(.*?)\s*(TEAM|WEBSITE)", text, re.DOTALL)
        data["Team Size"] = re.search(r"TEAM SIZE\s*(\d+)", text)
        data["Website"] = re.search(r"WEBSITE\s*(\S+)", text)
        data["Description"] = text.split("About")[-1].strip() if "About" in text else ""

        # Nettoyage
        return {
            "Name": data["Name"],
            "Pitch": data["Pitch"],
            "Founders": data["Founders"].group(1).strip().replace("\n", ", ") if data["Founders"] else "",
            "Year": data["Year"].group(1) if data["Year"] else "",
            "Categories": data["Categories"].group(1).strip().replace("\n", ", ") if data["Categories"] else "",
            "Team Size": data["Team Size"].group(1) if data["Team Size"] else "",
            "Website": data["Website"].group(1) if data["Website"] else "",
            "Description": data["Description"],
        }

    project_data = extract_data(fiche)
    st.session_state.projects.append(project_data)
    st.success(f"Projet « {project_data['Name']} » ajouté avec succès !")

# Affichage du tableau
if st.session_state.projects:
    df = pd.DataFrame(st.session_state.projects)
    st.subheader("📊 Projets extraits")
    st.dataframe(df, use_container_width=True)

    # Téléchargement
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger en CSV", csv, "projets.csv", "text/csv")
