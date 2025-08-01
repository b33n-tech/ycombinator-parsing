import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Parser Candidatures LinkedIn", layout="wide")

st.title("📄 LinkedIn - Parser multi-pages de candidatures")

st.markdown("""
Colle ici ton texte brut copié depuis LinkedIn (ex : page "Mes candidatures").  
**Chaque annonce doit idéalement être séparée par une ligne vide**.  
L’outil extrait automatiquement :

- ✅ Entreprise  
- ✅ Poste  
- ✅ Localisation  
- ✅ Statut complet (ex : "Candidature déposée il y a 2 j")  
- ✅ Tag simplifié ("Candidature déposée", "CV téléchargé", "Candidature vue")

Tu peux parser plusieurs pages d'affilée : elles seront toutes ajoutées dans un tableau final.

---
""")

# Session state init
if "candidatures" not in st.session_state:
    st.session_state["candidatures"] = []

if "corrected_text" not in st.session_state:
    st.session_state["corrected_text"] = ""

# Input brut
input_text = st.text_area("📋 Colle ici une page de candidatures :", height=300, key="original_text")

# ✨ Bouton pour corriger automatiquement les retours à la ligne
if st.button("↩️ Ajouter un saut de ligne après chaque statut reconnu"):
    if not input_text.strip():
        st.warning("Merci de coller du texte avant de corriger.")
    else:
        pattern = r"(Candidature déposée il y a .+?|CV téléchargé il y a .+?|Candidature vue il y a .+?)"
        corrected_text = re.sub(pattern, r"\1\n", input_text.strip())
        st.session_state["corrected_text"] = corrected_text
        st.success("Les sauts de ligne ont été ajoutés automatiquement.")

# Utiliser le texte corrigé s’il existe
source_text = st.session_state["corrected_text"] if st.session_state["corrected_text"] else input_text

# ➕ Ajout de la page au tableau
if st.button("➕ Ajouter cette page"):
    if not source_text.strip():
        st.warning("Merci de coller ou corriger du texte avant d’ajouter.")
    else:
        annonces = re.split(r"\n\s*\n", source_text.strip())
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
            st.success(f"{len(page_rows)} candidatures ajoutées avec succès.")
            st.session_state["corrected_text"] = ""  # reset après ajout
        else:
            st.warning("Aucune annonce valide détectée. Vérifie que le format est correct.")

# Affichage du tableau cumulé
if st.session_state["candidatures"]:
    st.markdown("---")
    st.subheader("🧾 Candidatures cumulées")
    df = pd.DataFrame(st.session_state["candidatures"])
    st.dataframe(df, use_container_width=True)

    # 📤 Export XLSX
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

    # 🔄 Reset
    if st.button("🗑️ Réinitialiser tout"):
        st.session_state["candidatures"] = []
        st.session_state["corrected_text"] = ""
        st.success("Toutes les candidatures ont été supprimées.")
