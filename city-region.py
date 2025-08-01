import streamlit as st
import pandas as pd

# --- Dictionnaire ville → région simplifié ---
ville_vers_region = {
    "paris": "Île-de-France",
    "neuilly-sur-seine": "Île-de-France",
    "puteaux": "Île-de-France",
    "lyon": "Auvergne-Rhône-Alpes",
    "strasbourg": "Grand Est",
    "lille": "Hauts-de-France",
    "bordeaux": "Nouvelle-Aquitaine",
    "toulouse": "Occitanie",
    "marseille": "Provence-Alpes-Côte d’Azur",
    "nantes": "Pays de la Loire",
    "rennes": "Bretagne",
    "nancy": "Grand Est",
    "dijon": "Bourgogne-Franche-Comté",
    "tours": "Centre-Val de Loire",
    "paray-vieille-poste": "Île-de-France",
    "grandvilliers": "Hauts-de-France",
    "versailles": "Île-de-France",
    "nice": "Provence-Alpes-Côte d’Azur",
    "montpellier": "Occitanie",
    "rouen": "Normandie",
    "caen": "Normandie"
    # ➕ Tu peux ajouter d'autres villes ici
}

# --- Fonction de nettoyage et correspondance ---
def nettoyer_localisation(loc):
    if pd.isna(loc):
        return "Localisation manquante"
    loc = str(loc).lower().split('(')[0].strip()
    return loc

def attribuer_region(loc, mapping):
    ville = nettoyer_localisation(loc)
    return mapping.get(ville, "Région inconnue")

# --- Interface Streamlit ---
st.title("Attribution automatique de région depuis une colonne de localisations")

# Upload du fichier
uploaded_file = st.file_uploader("Uploader un fichier Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("Fichier chargé avec succès.")
    st.write("Aperçu du fichier :", df.head())

    colonnes = df.columns.tolist()
    col_selection = st.selectbox("Sélectionnez la colonne contenant les localisations :", colonnes)

    if col_selection:
        df["Région attribuée"] = df[col_selection].apply(lambda x: attribuer_region(x, ville_vers_region))
        st.write("✅ Résultat avec régions attribuées :", df.head())

        # Téléchargement du fichier enrichi
        output = df.to_excel(index=False)
        st.download_button("📥 Télécharger le fichier enrichi", data=output, file_name="fichier_avec_regions.xlsx")
