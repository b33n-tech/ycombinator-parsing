import streamlit as st
import pandas as pd
import io
import re
from time import sleep

st.set_page_config(page_title="Parser Jobboard Station F", layout="centered")

st.title("📄 Parser des annonces de Station F")

# Choix du nombre de pages
num_pages = st.number_input("Nombre de pages que vous souhaitez copier-coller :", min_value=1, step=1)

# Création d'un espace pour stocker les textes
if "pages" not in st.session_state:
    st.session_state.pages = [""] * num_pages

# Affichage des zones de texte pour chaque page
for i in range(num_pages):
    st.session_state.pages[i] = st.text_area(f"Contenu de la page {i+1} :", value=st.session_state.pages[i], height=200)

# Bouton pour lancer le parsing
if st.button("📊 Lancer le parsing"):
    annonces = []
    total = len(st.session_state.pages)
    progress_bar = st.progress(0)

    for idx, page in enumerate(st.session_state.pages):
        # Nettoyage + séparation
        blocks = re.split(r'\n\s*\n', page.strip())

        for block in blocks:
            lines = block.strip().split("\n")
            if len(lines) >= 3:
                # Ligne 1 : "CDI - Intitulé"
                titre_type = lines[0].strip()
                startup = lines[1].strip()
                contrat = lines[2].strip()
                annonces.append({
                    "Titre": titre_type,
                    "Startup": startup,
                    "Contrat": contrat
                })

        progress_bar.progress((idx + 1) / total)
        sleep(0.1)  # Pour rendre la progression visible

    if not annonces:
        st.warning("Aucune annonce détectée. Vérifiez le format copié.")
    else:
        df = pd.DataFrame(annonces)
        st.success("Parsing terminé avec succès ✅")

        st.subheader("📋 Aperçu du tableau")
        st.dataframe(df)

        # Export Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Annonces")
        st.download_button("📥 Télécharger en .xlsx", data=output.getvalue(), file_name="annonces_stationf.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
