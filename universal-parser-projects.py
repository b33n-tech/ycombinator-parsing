import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Universal Project Parser", layout="wide")
st.title("🧠 Universal Project Parser")

st.markdown("""
Cet outil vous permet de parser un texte brut copié depuis un site web listant des projets, en extrayant automatiquement les informations selon les exemples que vous fournissez.

### Étapes :
1. Définissez les catégories d'information souhaitées (ex : Nom du projet, Pitch, Tags, Date, etc.).
2. Donnez pour chaque catégorie **un exemple précis**.
3. Copiez-collez l'ensemble du texte brut contenant plusieurs projets.
4. L'outil applique la logique aux blocs similaires.
5. Téléchargez le tableau `.xlsx` généré.
""")

# Step 1: Définition des catégories
st.subheader("1. Définir les catégories et exemples")
category_count = st.number_input("Combien de types d'information voulez-vous extraire ?", min_value=1, max_value=10, value=3, step=1)

categories = []
examples = []

for i in range(category_count):
    col1, col2 = st.columns(2)
    with col1:
        category = st.text_input(f"Nom de la catégorie #{i+1}", key=f"cat_{i}")
    with col2:
        example = st.text_input(f"Exemple correspondant à cette catégorie", key=f"ex_{i}")
    if category and example:
        categories.append(category.strip())
        examples.append(example.strip())

# Step 2: Texte complet à parser
st.subheader("2. Copier-coller le texte contenant tous les projets")
raw_text = st.text_area("Texte brut copié depuis un site web", height=400)

# Step 3: Lancer le parsing
st.subheader("3. Résultat et export")
if st.button("Lancer le parsing"):
    if not raw_text or not categories or not examples:
        st.error("Veuillez remplir tous les champs nécessaires.")
    else:
        # Construction des regex dynamiques à partir des exemples
        lines = raw_text.splitlines()

        blocks = []
        block = []
        for line in lines:
            if line.strip() == "":
                if block:
                    blocks.append("\n".join(block))
                    block = []
            else:
                block.append(line.strip())
        if block:
            blocks.append("\n".join(block))

        df = pd.DataFrame(columns=categories)

        for b in blocks:
            row = {}
            for cat, ex in zip(categories, examples):
                pattern = re.escape(ex)
                match = re.search(pattern, b, flags=re.IGNORECASE)
                if match:
                    row[cat] = match.group()
                else:
                    row[cat] = ""
            df.loc[len(df)] = row

        st.dataframe(df)

        # Export as XLSX
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Parsed')
            writer.save()
            processed_data = output.getvalue()

        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=processed_data,
            file_name="parsed_projects.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
