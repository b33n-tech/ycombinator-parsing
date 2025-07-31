import streamlit as st
import pandas as pd
import re

st.title("🏷️ Tag Expander → One Column → Many")

st.markdown("""
Charge un fichier CSV **ou** colle un tableau avec une colonne contenant des **tags séparés par virgule ou point-virgule**.

Ce script crée automatiquement **une colonne par tag**, et te permet de le télécharger au format CSV.
""")

uploaded_file = st.file_uploader("📁 Charge un fichier CSV", type=["csv"])
manual_input = st.text_area("... ou colle un tableau CSV (optionnel)", height=300)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif manual_input:
    from io import StringIO
    df = pd.read_csv(StringIO(manual_input))
else:
    st.stop()

tag_col_name = st.selectbox("📌 Choisis la colonne contenant les tags :", df.columns)

if st.button("🚀 Générer colonnes par tag"):
    # Normaliser les séparateurs et nettoyer les tags
    def clean_split(tags):
        if pd.isna(tags):
            return []
        split_tags = re.split(r"[;,]", tags)
        return [tag.strip() for tag in split_tags if tag.strip()]

    df["__split_tags__"] = df[tag_col_name].apply(clean_split)

    # Récupérer tous les tags uniques
    all_tags = sorted(set(tag for tags in df["__split_tags__"] for tag in tags))

    # Ajouter une colonne par tag
    for tag in all_tags:
        df[tag] = df["__split_tags__"].apply(lambda tags: int(tag in tags))

    df.drop(columns=["__split_tags__"], inplace=True)

    st.success(f"{len(all_tags)} colonnes de tags créées avec succès.")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger le fichier final", csv, "expanded_tags.csv", "text/csv")
