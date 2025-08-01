import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("🔖 Outil d'attribution de tags par mots-clés")

# 1. Upload du fichier
uploaded_file = st.file_uploader("Charge ton fichier Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Aperçu du fichier :", df.head())

    # 2. Choix de la colonne
    selected_col = st.selectbox("Choisis la colonne à analyser :", df.columns)

    # 3. Création dynamique des tags
    st.markdown("### 🎯 Définis tes tags (5 à 7 max)")
    nb_tags = st.slider("Nombre de tags à définir", 1, 7, 3)
    
    tags_config = []
    for i in range(nb_tags):
        st.markdown(f"**Tag {i+1}**")
        cat = st.text_input(f"Catégorie du Tag {i+1}", key=f"cat_{i}")
        name = st.text_input(f"Nom du Tag {i+1}", key=f"name_{i}")
        keywords = st.text_area(f"Mots-clés (séparés par virgule)", key=f"kw_{i}")
        if cat and name and keywords:
            tag_fullname = f"{cat}/{name}"
            kw_list = [kw.strip().lower() for kw in keywords.split(",") if kw.strip()]
            tags_config.append((tag_fullname, kw_list))

    if st.button("🔍 Appliquer les tags"):
        result_df = df.copy()
        col_to_check = df[selected_col].astype(str).str.lower()

        for tag_fullname, keywords in tags_config:
            # Création d'une nouvelle colonne avec True/False si un des mots-clés est détecté
            result_df[tag_fullname] = col_to_check.apply(
                lambda text: any(re.search(rf"\b{kw}\b", text, re.IGNORECASE) for kw in keywords)
            )

        st.success("Tags appliqués avec succès !")
        st.dataframe(result_df.head())

        # Export en Excel
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Tagged')
            return output.getvalue()

        st.download_button(
            label="📥 Télécharger le fichier avec tags",
            data=to_excel(result_df),
            file_name="tagged_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
