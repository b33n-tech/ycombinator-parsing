import streamlit as st
import pandas as pd
import io

# Dictionnaire de correspondance ville → région (extrait, à compléter selon ton besoin)
ville_vers_region = {
    "Paris": "Île-de-France",
    "Lyon": "Auvergne-Rhône-Alpes",
    "Marseille": "Provence-Alpes-Côte d'Azur",
    "Puteaux": "Île-de-France",
    "Neuilly-sur-Seine": "Île-de-France",
    "Paray-Vieille-Poste": "Île-de-France",
    "Grandvilliers": "Hauts-de-France",
}

# Fonction pour attribuer une région à partir de la ville détectée dans le champ
def attribuer_region(localisation, ville_vers_region):
    if pd.isna(localisation):
        return ""
    for ville in ville_vers_region:
        if ville.lower() in localisation.lower():
            return ville_vers_region[ville]
    return "Non reconnu"

st.title("📍 Attribution automatique des régions à partir de la localisation")

# Upload de fichier
fichier = st.file_uploader("📤 Upload ton fichier Excel", type=["xlsx"])

if fichier:
    df = pd.read_excel(fichier)
    st.write("✅ Aperçu du fichier :", df.head())

    # Sélection de la colonne contenant les localisations
    colonnes = df.columns.tolist()
    col_selection = st.selectbox("🧭 Choisis la colonne de localisation", colonnes)

    if col_selection:
        df["Région attribuée"] = df[col_selection].apply(lambda x: attribuer_region(x, ville_vers_region))
        st.write("✅ Résultat avec régions attribuées :", df.head())

        # Génération Excel en mémoire
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)

        st.download_button(
            label="📥 Télécharger le fichier enrichi",
            data=output,
            file_name="fichier_avec_regions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
