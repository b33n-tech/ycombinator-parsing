import streamlit as st
import pandas as pd
import re

st.title("🚀 Scraper Founder Inc - Extracteur de Startups")

st.markdown("Colle ici le texte copié du site Founder Inc. avec les noms, tags et pitchs (format brut).")

raw_input = st.text_area("📋 Coller ici :", height=300)

if st.button("🔍 Extraire"):
    if not raw_input.strip():
        st.warning("Merci de coller du contenu avant de lancer l'extraction.")
    else:
        lines = raw_input.split("\n")
        words = [word.strip() for line in lines for word in line.strip().split("  ") if word.strip()]

        startups = []
        i = 0
        while i < len(words) - 1:
            name = words[i]
            tags = []
            i += 1
            # collect tags until we hit the pitch (assumed to have punctuation or be a complete sentence)
            while i < len(words) and not re.search(r"[.!?]$", words[i]) and len(words[i].split()) <= 5:
                tags.append(words[i])
                i += 1
            pitch = words[i] if i < len(words) else ""
            startups.append({
                "Startup Name": name,
                "Tags": ", ".join(tags),
                "Pitch": pitch
            })
            i += 1

        df = pd.DataFrame(startups)
        st.success(f"{len(df)} startups extraites.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger en CSV", csv, "startups_founder_inc.csv", "text/csv")
