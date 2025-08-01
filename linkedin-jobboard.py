import streamlit as st
import re
import pandas as pd

st.title("🧹 LinkedIn - Parser de candidatures")

st.markdown("""
Copie-colle ici les candidatures brutes depuis LinkedIn.  
L’outil extrait automatiquement :
- Le **nom de l'entreprise**
- Le **poste**
- La **localisation**
- Le **statut** (ex: Candidature déposée, Candidature vue, etc.)
""")

input_text = st.text_area("📋 Colle ici ton texte brut LinkedIn :", height=300)

if st.button("🧪 Parser les candidatures"):
    if not input_text.strip():
        st.warning("Merci de coller du texte avant de parser.")
    else:
        # On découpe les blocs en supposant qu'ils sont séparés par deux retours à la ligne
        blocks = re.split(r"\n(?=\S)", input_text.strip())
        rows = []

        for i in range(0, len(blocks)-2, 4):  # Chaque bloc de 4 lignes
            try:
                entreprise = blocks[i].strip()
                poste = blocks[i+1].strip()
                localisation = blocks[i+3].strip() if "Candidature" not in blocks[i+3] else blocks[i+2].strip()
                statut = blocks[i+3] if "Candidature" in blocks[i+3] else blocks[i+4]
                rows.append({
                    "Entreprise": entreprise,
                    "Poste": poste,
                    "Localisation": localisation,
                    "Statut": statut
                })
            except IndexError:
                continue

        if rows:
            df = pd.DataFrame(rows)
            st.success(f"{len(df)} candidatures extraites !")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Télécharger en CSV", data=csv, file_name="candidatures_parsées.csv", mime="text/csv")
        else:
            st.warning("Aucune donnée extraite. Le format n’est peut-être pas conforme.")
