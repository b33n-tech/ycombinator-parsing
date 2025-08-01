import streamlit as st
import pandas as pd
import re
from io import StringIO, BytesIO

st.title("🏷️ Tag Expander → One Column → Many")

st.markdown("""
Charge un fichier **CSV ou XLSX**, ou colle un tableau avec une colonne contenant des **tags séparés par virgule ou point-virgule**.

Ce script crée automatiquement **une colonne par tag**, et te permet de télécharger le fichier transformé.
""")

uploaded_file = st.file_uploader("📁 Charge un fichier CSV ou XLSX", type=["csv", "xlsx"])
manual_input = st.text_area("... ou colle un tableau CSV (optionnel)", height=300)

df = None
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
elif manual_input:
    df = pd.read_csv(StringIO(manual_input))

if df is None:
    st.stop()

tag_col_name = st.selectbox("📌 Choisis la colonne contenant les tags :", df.columns)

if st.button("🚀 Générer colonnes par tag"):
    # Fonction pour nettoyer et séparer les tags
    def clean_split(tags):
        if pd.isna(tags):
            return []
        split_tags = re.split(r"[;,]", str(tags))
        return [tag.strip() for tag in split_tags if tag.strip()]

    df["__split_tags__"] = df[tag_col_name].apply(clean_split)

    all_tags = sorted(set(tag for tags in df["__split_tags__"] for tag in tags))

    for tag in all_tags:
        df[tag] = df["__split_tags__"].apply(lambda tags: int(tag in tags))

    df.drop(columns=["__split_tags__"], inplace=True)

    st.success(f"{len(all_tags)} colonnes de tags créées avec succès.")
    st.dataframe(df)

    # Export CSV
    csv_data = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Télécharger en CSV", csv_data, "expanded_tags.csv", "text/csv")

    # Export XLSX
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
    st.download_button("📥 Télécharger en XLSX", excel_buffer.getvalue(), "expanded_tags.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
