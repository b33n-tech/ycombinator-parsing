import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("Parsing d'annonces B2B")

# Initialisation de l'état de session
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "pages" not in st.session_state:
    st.session_state.pages = [""] * st.session_state.num_pages
if "parsed_data" not in st.session_state:
    st.session_state.parsed_data = []

# Choix du nombre de pages
num_pages = st.number_input("Nombre de pages que vous allez coller :", min_value=1, max_value=20, value=st.session_state.num_pages, step=1)

# Mise à jour dynamique de pages si le nombre change
if num_pages != st.session_state.num_pages:
    st.session_state.num_pages = num_pages
    st.session_state.pages = [""] * num_pages

# Input des pages
for i in range(st.session_state.num_pages):
    st.session_state.pages[i] = st.text_area(f"Contenu de la page {i+1} :", value=st.session_state.pages[i], height=200)

def parse_announcements(text):
    # Nettoyage et séparation des blocs d'annonces
    blocks = re.split(r"\n\s*\n", text.strip())
    results = []

    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        if len(lines) >= 3:
            # Extraction
            contrat_titre = lines[0]
            startup = lines[1]
            contrat_type = lines[2]
            results.append({
                "Type de contrat + Intitulé": contrat_titre,
                "Startup": startup,
                "Contrat (Full-time etc)": contrat_type
            })
    return results

# Traitement au clic
if st.button("Lancer le parsing"):
    all_data = []
    total_pages = st.session_state.num_pages

    # Affiche la barre de progression
    progress_bar = st.progress(0)
    for i, page_text in enumerate(st.session_state.pages):
        parsed = parse_announcements(page_text)
        all_data.extend(parsed)
        progress_bar.progress((i + 1) / total_pages)

    df = pd.DataFrame(all_data)
    st.session_state.parsed_data = df
    st.success(f"{len(df)} annonces extraites avec succès.")

# Affichage des résultats si présents
if isinstance(st.session_state.parsed_data, pd.DataFrame) and not st.session_state.parsed_data.empty:
    st.subheader("Tableau des annonces extraites :")
    st.dataframe(st.session_state.parsed_data)

    # Téléchargement XLSX
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Annonces')
        return output.getvalue()

    st.download_button(
        label="📥 Télécharger en .xlsx",
        data=to_excel(st.session_state.parsed_data),
        file_name="annonces_parsées.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
