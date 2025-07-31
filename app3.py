import streamlit as st
import pandas as pd
import io

st.title("📄 Parser Offres Station F → Excel (version 3 lignes)")

st.markdown("""
Colle ici le contenu copié du jobboard Station F (même plusieurs pages).  
Chaque offre doit être sur **3 lignes consécutives** :
1. Type de contrat + Intitulé du poste  
2. Nom de la startup  
3. Type de poste (Full-Time, Internship, etc)
""")

raw_text = st.text_area("📋 Colle ici le texte brut :", height=400)

def parse_three_line_jobs(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    jobs = []

    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            contrat_titre = lines[i]
            startup = lines[i+1]
            type_poste = lines[i+2]

            # Optionnel : séparer "CDI - Intitulé" en deux colonnes
            if " - " in contrat_titre:
                contrat, titre = contrat_titre.split(" - ", 1)
            else:
                contrat = ""
                titre = contrat_titre

            jobs.append({
                "Type de contrat": contrat.strip(),
                "Titre du poste": titre.strip(),
                "Startup": startup,
                "Type de poste": type_poste
            })

    return pd.DataFrame(jobs)

if raw_text:
    df = parse_three_line_jobs(raw_text)
    st.success(f"{len(df)} offres détectées !")
    st.dataframe(df)

    # Export en Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Offres')
    st.download_button(
        label="📥 Télécharger Excel",
        data=buffer.getvalue(),
        file_name="offres_stationf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
