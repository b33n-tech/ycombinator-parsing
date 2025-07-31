import streamlit as st
import pandas as pd
import re

st.title("🧠 Intelligent Startup Extractor - Founder Inc")

st.markdown("""
Colle ci-dessous le contenu brut du site Founder Inc.
L’outil détecte dynamiquement : **Nom**, **Tags**, **Pitch**
""")

raw_text = st.text_area("✂️ Collez le texte ici :", height=400)

def is_probably_name(line):
    # A name is usually capitalized and short (not a full sentence)
    return bool(re.match(r"^[A-Z][a-zA-Z0-9&()\-\s']+$", line)) and len(line.split()) <= 4

def is_probably_pitch(line):
    return bool(re.search(r"[.!?]$", line)) or len(line.split()) > 5

if st.button("🔍 Extraire"):
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    
    startups = []
    current_name = None
    current_tags = []
    current_pitch = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]

        # Nouvelle startup détectée
        if is_probably_name(line) and (i == 0 or is_probably_pitch(lines[i-1])):
            if current_name:
                # Sauvegarder le précédent projet
                startups.append({
                    "Startup Name": current_name,
                    "Tags": ", ".join(current_tags),
                    "Pitch": current_pitch
                })
            # Réinitialiser
            current_name = line
            current_tags = []
            current_pitch = ""
            i += 1
            continue

        # Si ligne ressemble à un tag
        if not is_probably_pitch(line):
            current_tags.append(line)
        else:
            current_pitch = line
        
        i += 1

    # Ajouter le dernier projet
    if current_name:
        startups.append({
            "Startup Name": current_name,
            "Tags": ", ".join(current_tags),
            "Pitch": current_pitch
        })

    df = pd.DataFrame(startups)
    st.success(f"{len(df)} startups extraites.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger en CSV", csv, "startups_founder_inc.csv", "text/csv")

