import streamlit as st
import re
import pandas as pd

st.title("📄 LinkedIn - Parser de candidatures")

st.markdown("""
Colle ici ton texte brut copié depuis LinkedIn.  
Chaque annonce doit être **séparée par une ligne vide** (saut de ligne entre deux annonces).

L’outil va extraire automatiquement :
- ✅ **Nom de l'entreprise**
- ✅ **Poste**
- ✅ **Localisation**
- ✅ **Statut de la candidature**
""")

input_text = st.text_area("✂️ Texte brut LinkedIn :", height=300)

if st.button("🔍 Lancer le parsing"):
    if not input_text.strip():
        st.warning("Merci de coller du texte avant de parser.")
    else:
        annonces = re.split(r"\n\s*\n", input_text.strip())  # Sépare par sauts de ligne multiples
        rows = []

        for annonce in annonces:
            lignes = [line.strip() for line in annonce.strip().split("\n") if line.strip()]
            
            if len(lignes) >= 4:
                entreprise = lignes[0]
                poste = lignes[1]
                localisation = ""
                statut = ""

                # On cherche automatiquement la ligne avec "Sur site", "Hybride", etc.
                for ligne in lignes:
                    if re.search(r"(Sur site|Hybride|Remote|Paris|Lyon|Area)", ligne, re.IGNORECASE):
                        localisation = ligne
                    if "Candidature" in ligne or "CV téléchargé" in ligne:
                        statut = ligne

                rows.append({
                    "Entreprise": entreprise,
                    "Poste": poste,
                    "Localisation": localisation,
                    "Statut": statut
                })

        if rows:
            df = pd.DataFrame(rows)
            st.success(f"{len(df)} candidatures extraites avec succès !")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger le CSV", data=csv, file_name="candidatures_parsées.csv", mime="text/csv")
        else:
            st.warning("Aucune donnée extraite. Vérifie que les annonces sont bien séparées par une ligne vide.")
