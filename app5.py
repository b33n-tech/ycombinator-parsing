import streamlit as st
import pandas as pd

# Liste complète des tags utilisés sur le site Founder Inc
KNOWN_TAGS = {
    "AI/ML", "Hardware", "Consumer", "Devtools", "Web3", "AR/VR", "Gaming", "B2B"
}

st.title("🚀 Scraper intelligent - Founder Inc. Portfolio")

st.markdown("""
Colle ici **le texte brut** du site [foundersinc.com/portfolio](https://foundersinc.com/portfolio) — l'outil extrait :
- **Nom de la startup**
- **Tags** (selon la liste complète intégrée)
- **Pitch**
""")

raw_text = st.text_area("📝 Copie le texte ici :", height=500)

if st.button("🔍 Extraire les startups"):
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    startups = []
    i = 0

    while i < len(lines):
        name = lines[i]
        i += 1

        tags = []
        # Collecter tous les tags consécutifs
        while i < len(lines) and lines[i] in KNOWN_TAGS:
            tags.append(lines[i])
            i += 1

        # Pitch : la première ligne après les tags
        pitch = lines[i] if i < len(lines) else ""
        i += 1

        # On vérifie que c'est bien une startup avec tag ou pitch pour ne pas enregistrer du bruit
        if tags or pitch:
            startups.append({
                "Startup Name": name,
                "Tags": ", ".join(tags),
                "Pitch": pitch
            })

    if startups:
        df = pd.DataFrame(startups)
        st.success(f"{len(df)} startups extraites.")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger CSV", csv, "founder_portfolio.csv", "text/csv")
    else:
        st.warning("Aucune startup détectée. Vérifie le format et que tu as bien inclus les tags/pitchs.")
