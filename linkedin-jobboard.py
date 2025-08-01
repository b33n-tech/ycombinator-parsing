import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Parser Candidatures LinkedIn", layout="wide")

st.title("📄 LinkedIn - Parser multi-pages de candidatures")

st.markdown("""
Colle ici ton texte brut (copié depuis une ou plusieurs pages de LinkedIn).  
**Chaque annonce doit être séparée par une ligne vide**.

Tu peux parser plusieurs pages, elles seront toutes ajoutées dans un tableau final unique.  
L’outil va extraire :

- ✅ Nom de l'entreprise  
- ✅ Poste  
- ✅ Localisation  
- ✅ Statut complet (ex: "Candidature déposée il y a 3 j")  
- ✅ Tag automatique : "Candidature déposée", "CV téléchargé" ou "Candidature vue"

---
""")

if "candidatures" not in st.session_state:
    st.session_state["candidatures"] = []

input_text = st.text_area("📋 Colle ici une page de candidatures :", height=300)

if st.button("➕ Ajouter cette page"):
    if not input_text.strip():
        st.warning("Merci de coller du texte avant de parser.")
    else:
        annonces = re.split(r"\n\s*\n", input_text.strip())
        page_rows = []

        for annonce in annonces:
            lignes = [line.strip() for line in annonce.strip().split("\n") if line.strip()]
            
            if len(lignes) >= 4:
                entreprise = lignes[0]
                poste = lignes[1]
                localisation = ""
                statut_complet = ""
                tag = ""

                for ligne in lignes:
                    if re.search(r"(Sur site|Hybride|Remote|Paris|Lyon|Area)", ligne, re.IGNORECASE):
                        localisation = ligne
                    if "Candidature" in ligne or "CV téléchargé" in ligne:
                        statut_complet = ligne
                        if ligne.startswith("Candidature déposée"):
                            tag = "Candidature déposée"
                        elif ligne.startswith("CV téléchargé"):
                            tag = "CV téléchargé"
                        elif ligne.startswith("Candidature vue"):
                            tag = "Candidature vue"

                page_rows.append({
                    "Entreprise": entreprise,
                    "Poste": poste,
                    "Localisation": localisation,
                    "Statut": statut_complet,
                    "Tag": tag
                })

        if page_rows:
            st.session_state["candidatures"].extend(page_rows)
            st.success(f"{len(page_rows)} candidatures ajoutées.")
        else:
            st.warning("Aucune annonce valide détectée. Vérifie le format.")

# Affichage du tableau cumulé
if st.session_state["candidatures"]:
    st.markdown("---")
    st.subheader("🧾 Tableau cumulé des candidatures")
    df = pd.DataFrame(st.session_state["candidatures"])
    st.dataframe(df, use_container_width=True)

    # Export XLSX
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Candidatures")
    output.seek(0)

    st.download_button(
        label="📥 Télécharger en .xlsx",
        data=output,
        file_name="candidatures_linkedin.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🗑️ Réinitialiser tout"):
        st.session_state["candidatures"] = []
        st.success("Toutes les candidatures ont été supprimées.")
