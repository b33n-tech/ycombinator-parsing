import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Parser Candidatures LinkedIn", layout="wide")
st.title("📄 LinkedIn - Parser multi-pages de candidatures")

st.markdown("""
Colle ici ton texte brut copié depuis LinkedIn.  
**Chaque annonce doit être séparée par une ligne vide** (saut de ligne).  
Tu peux parser plusieurs pages l’une après l’autre. Les candidatures s'accumulent dans un tableau final.

Fonctionnalités :
- ✅ Extraction automatique : entreprise, poste, localisation, statut
- ✅ Tag automatique : *Candidature déposée*, *CV téléchargé*, *Candidature vue*
- ✅ Bouton magique : ajoute un saut de ligne après chaque statut
- ✅ Export global en `.xlsx`

---
""")

# État session : stockage de toutes les candidatures
if "candidatures" not in st.session_state:
    st.session_state["candidatures"] = []

# Texte brut à coller
input_text = st.text_area("📋 Colle ici une page de candidatures LinkedIn :", height=300, key="original_text")

# Bouton magique : ajoute un saut de ligne après les statuts
if st.button("↩️ Ajouter un saut de ligne après chaque statut reconnu"):
    if not st.session_state.original_text.strip():
        st.warning("Merci de coller du texte avant d'utiliser cette fonction.")
    else:
        pattern = r"(Candidature déposée il y a .*?|CV téléchargé il y a .*?|Candidature vue il y a .*?)"
        corrected_text = re.sub(pattern, r"\1\n", st.session_state.original_text.strip())
        st.session_state["corrected_text"] = corrected_text
        st.text_area("✅ Texte corrigé :", corrected_text, height=300, key="text_corrigé")
        st.info("Sauts de ligne ajoutés après les statuts.")
    st.stop()  # Ne pas continuer le parsing dans ce cas

# Parsing du texte (corrigé si dispo, sinon original)
if st.button("➕ Ajouter cette page au tableau final"):
    source_text = st.session_state.get("corrected_text", st.session_state.original_text)

    if not source_text.strip():
        st.warning("Merci de coller du texte avant de parser.")
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
                    if re.match(r"(Candidature déposée|CV téléchargé|Candidature vue) il y a ", ligne):
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
            st.warning("Aucune annonce valide détectée. Vérifie que les annonces sont bien séparées.")

# Affichage et export
if st.session_state["candidatures"]:
    st.markdown("---")
    st.subheader("🧾 Tableau cumulé des candidatures")
    df = pd.DataFrame(st.session_state["candidatures"])
    st.dataframe(df, use_container_width=True)

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

    if st.button("🗑️ Réinitialiser toutes les candidatures"):
        st.session_state["candidatures"] = []
        st.success("Toutes les candidatures ont été réinitialisées.")
