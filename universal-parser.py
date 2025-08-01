import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Système de Tags", layout="centered")
st.title("🏷️ Attribution automatique de tags par mots-clés")
st.markdown("Téléverse un fichier Excel et applique automatiquement des tags en fonction de mots-clés que tu définis.")

# 1. Upload du fichier
uploaded_file = st.file_uploader("📂 Charge un fichier Excel (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Fichier chargé avec succès ✅")
    st.write("Aperçu des premières lignes :", df.head())

    # 2. Sélection de la colonne à analyser
    selected_col = st.selectbox("🧩 Sélectionne la colonne à analyser :", df.columns)

    # 3. Définition des tags
    st.markdown("### 🏗️ Configuration des tags à appliquer")
    nb_tags = st.slider("Nombre de tags à définir :", 1, 7, 3)

    tags_config = []
    for i in range(nb_tags):
        with st.expander(f"📝 Tag {i+1}"):
            cat = st.text_input(f"Catégorie du Tag {i+1}", key=f"cat_{i}")
            name = st.text_input(f"Nom du Tag {i+1}", key=f"name_{i}")
            keywords_input = st.text_area(
                f"Mots-clés déclencheurs (séparés par des virgules)", 
                key=f"kw_{i}",
                placeholder="ex : lyon, marseille, lille"
            )

            if cat and name and keywords_input:
                tag_label = f"{cat}/{name}"
                keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]
                tags_config.append((tag_label, keywords))

    # 4. Application des tags
    if st.button("🚀 Appliquer les tags"):
        result_df = df.copy()
        col_to_check = result_df[selected_col].astype(str).str.lower()

        for tag_label, keywords in tags_config:
            result_df[tag_label] = col_to_check.apply(
                lambda text: any(kw in text for kw in keywords)
            )

        st.success("Tags appliqués avec succès 🎉")
        st.dataframe(result_df.head())

        # 5. Export XLSX
        def convert_df_to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name="Tags", index=False)
            return output.getvalue()

        excel_data = convert_df_to_excel(result_df)

        st.download_button(
            label="📥 Télécharger le fichier taggé (.xlsx)",
            data=excel_data,
            file_name="fichier_taggé.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Charge un fichier Excel pour commencer.")
