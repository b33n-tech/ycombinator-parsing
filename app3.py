import streamlit as st
import pandas as pd
import io
import re

st.title("📄 Parser d'Offres Station F → Excel")

st.markdown("""
Colle ici le contenu copié du jobboard Station F (une ou plusieurs pages).  
L'app extraira automatiquement les **titres de postes**, **noms d'entreprises** et **types de contrat**.
""")

raw_text = st.text_area("📋 Colle ici le texte brut :", height=400)

def parse_jobs(text):
    # On découpe par double saut de ligne, typique d'un bloc d'offre
    blocks = re.split(r'\n{2,}', text.strip())
    jobs = []

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            title = lines[0].strip()
            company = lines[1].strip()
            job_type = lines[2].strip()
            jobs.append({
                'Titre du poste': title,
                'Entreprise': company,
                'Type de contrat': job_type
            })
    return pd.DataFrame(jobs)

if raw_text:
    df = parse_jobs(raw_text)
    st.success(f"{len(df)} offres détectées !")
    st.dataframe(df)

    # Téléchargement du fichier
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Jobs')
    st.download_button(
        label="📥 Télécharger en Excel",
        data=buffer.getvalue(),
        file_name="stationf_jobs.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
