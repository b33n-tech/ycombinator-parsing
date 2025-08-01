import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("🧠 Universal Project Parser")
st.markdown("Collez ici le texte brut copié depuis une page listant des projets. Vous pouvez aussi fournir un exemple structuré pour aider le parsing.")

example_input = st.text_area("Exemple de fiche projet (au moins une)", placeholder="Nom du projet\nTags séparés par virgules\nDate éventuelle\nPitch...", height=200)
raw_text = st.text_area("Texte à parser (copié depuis une page web)", height=400)

# Fonctions utilitaires de parsing
def detect_project_blocks(text, example_structure):
    if example_structure:
        example_lines = [line.strip() for line in example_structure.strip().split("\n") if line.strip()]
        n_lines = len(example_lines)
        raw_lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        blocks = ["\n".join(raw_lines[i:i+n_lines]) for i in range(0, len(raw_lines), n_lines)]
        return blocks
    else:
        blocks = re.split(r"\n{2,}", text.strip())
        return [b.strip() for b in blocks if b.strip()]

def parse_block(block, example_structure):
    lines = block.split("\n")
    name = lines[0] if len(lines) > 0 else ""
    tags = ""
    date = ""
    pitch = ""

    for i, line in enumerate(lines[1:], start=1):
        if re.search(r"\d{4}|Q[1-4]|[Jj]anuary|[Ff]ebruary|[Mm]arch|[Aa]pril|[Mm]ay|[Jj]une|[Jj]uly|[Aa]ugust|[Ss]eptember|[Oo]ctober|[Nn]ovember|[Dd]ecember", line):
            date = line.strip()
        elif ("," in line or ";" in line) and len(line.split()) <= 15:
            tags = line.strip()
        else:
            pitch += line.strip() + " "

    return {
        "Nom": name,
        "Tags": tags,
        "Date": date,
        "Pitch": pitch.strip()
    }

# Traitement principal
if st.button("🚀 Parser le texte") and raw_text:
    blocks = detect_project_blocks(raw_text, example_input)
    parsed_data = [parse_block(b, example_input) for b in blocks]
    df = pd.DataFrame(parsed_data)

    st.success(f"✅ {len(df)} projets détectés.")
    st.dataframe(df, use_container_width=True, height=600)

    # Option de téléchargement Excel
    def convert_df_to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Projets')
        return output.getvalue()

    excel_data = convert_df_to_excel(df)
    st.download_button(
        label="📥 Télécharger en Excel",
        data=excel_data,
        file_name="projets_parsés.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

elif not raw_text:
    st.info("Collez le contenu d’une page web pour commencer.")
