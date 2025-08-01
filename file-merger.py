import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Fusionneur de fichiers Excel", layout="wide")

st.title("🧩 Fusionneur de fichiers Excel (.xlsx)")

st.markdown("""
Charge ici plusieurs fichiers Excel **ayant les mêmes colonnes** :  
👉 L'outil les fusionnera **en une seule feuille unique** (pas plusieurs onglets).

- Format attendu : `.xlsx`
- Fusion ligne par ligne (concat verticale)
""")

# Upload multiple de fichiers
uploaded_files = st.file_uploader("📂 Glisser-déposer tes fichiers Excel ici :", type="xlsx", accept_multiple_files=True)

if uploaded_files:
    all_dfs = []
    base_columns = None
    error = False

    for file in uploaded_files:
        try:
            df = pd.read_excel(file)
            if base_columns is None:
                base_columns = list(df.columns)
            elif list(df.columns) != base_columns:
                st.error(f"❌ Le fichier {file.name} n'a pas les mêmes colonnes que les autres.")
                error = True
                break
            all_dfs.append(df)
        except Exception as e:
            st.error(f"Erreur lors de la lecture de {file.name} : {e}")
            error = True
            break

    if not error and all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        st.success(f"{len(uploaded_files)} fichiers fusionnés avec succès.")
        st.dataframe(merged_df, use_container_width=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            merged_df.to_excel(writer, index=False, sheet_name="Fusion")
        output.seek(0)

        st.download_button(
            label="📥 Télécharger le fichier fusionné (.xlsx)",
            data=output,
            file_name="fichier_fusionne.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
