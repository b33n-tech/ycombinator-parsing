import streamlit as st
import pandas as pd
import re

# Définir les localisations connues
localisations_connues = [
    "Lormont", "Greater Nancy Area", "Neyron", "Saint-Didier-sur-Chalaronne", "Le Mans", "Île-de-France", "Châtillon",
    "La Rochelle", "Palaiseau", "Occitanie", "La Courneuve", "Greater Rennes Metropolitan Area", "Greater Strasbourg Metropolitan Area",
    "Nancy", "Haute-Savoie", "Bordeaux", "Nice", "Ambilly", "Strasbourg", "Clermont-Ferrand", "Tours",
    "La Chapelle-sur-Erdre", "Ouges", "Lingolsheim", "Bastia", "Saint-Félix", "Reims", "Gérardmer", "Villeurbanne",
    "St.-Fons", "Neuilly-sur-Marne", "Erstein", "Gap", "Marlenheim", "Briançon", "Rouen", "Annecy", "Valence",
    "Greater Bordeaux Metropolitan Area", "Noisy-le-Grand", "Grigny", "Aix-en-Provence", "Maritime Alps",
    "Bry-sur-Marne", "Roissy-en-France", "Chenôve", "Versailles", "Le Plessis-Trévise", "Granville", "Troyes",
    "Dijon", "Blanquefort", "Lille", "Castelnau-le-Lez", "Toulouse", "Villenave-d’Ornon", "Monswiller", "Bayeux",
    "Greater Nantes Metropolitan Area", "Rennes", "La Garde", "Rodez", "Angers", "Illkirch-Graffenstaden",
    "Lons-le-Saunier", "Greater Toulouse Metropolitan Area", "Laxou", "Compiègne", "Montaigu-Vendée",
    "Greater Lille Metropolitan Area", "Colmar", "Boulogne-Billancourt", "Rueil-Malmaison", "Molsheim",
    "Beaupréau-en-Mauges", "Levallois-Perret", "Bondoufle", "Fontaine-lès-Dijon", "Amsterdam Area", "Marseille"
]

# Nettoyer les localisations (ex: "Strasbourg (Hybride)" -> "Strasbourg")
def nettoyer_localisation(texte):
    if pd.isna(texte):
        return ""
    # Supprimer les parenthèses et tout ce qu'elles contiennent
    texte = re.sub(r"\s*\(.*?\)", "", texte)
    texte = texte.strip()
    return texte

# Fonction de correspondance avec la liste
def trouver_localisation_propre(texte):
    for loc in localisations_connues:
        if loc.lower() in texte.lower():
            return loc
    return "Non reconnu"

# App Streamlit
st.title("🗺️ Nettoyeur de Localisations LinkedIn")

# Upload
uploaded_file = st.file_uploader("📤 Upload ton fichier Excel ou CSV", type=["xlsx", "xls", "csv"])
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.success("✅ Fichier chargé avec succès.")
    colonnes = df.columns.tolist()
    col_loc = st.selectbox("📍 Sélectionne la colonne des localisations", colonnes)

    if col_loc:
        # Nettoyer les localisations
        df["localisation_clean"] = df[col_loc].apply(nettoyer_localisation)
        # Associer aux localisations connues
        df["localisation_finale"] = df["localisation_clean"].apply(trouver_localisation_propre)

        st.write("🔎 Aperçu des localisations détectées :")
        st.dataframe(df[[col_loc, "localisation_clean", "localisation_finale"]].head(30))

        # Téléchargement
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode("utf-8")

        csv = convert_df(df)
        st.download_button(
            label="💾 Télécharger les résultats au format CSV",
            data=csv,
            file_name="localisations_nettoyees.csv",
            mime="text/csv",
        )
