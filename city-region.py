import streamlit as st
import pandas as pd

# === Dictionnaire de correspondance villes/zones -> régions ===
location_to_region = {
    "paris": "Île-de-France",
    "greater paris metropolitan region": "Île-de-France",
    "neuilly-sur-seine": "Île-de-France",
    "puteaux": "Île-de-France",
    "versailles": "Île-de-France",
    "rueil-malmaison": "Île-de-France",
    "noisy-le-grand": "Île-de-France",
    "boulogne-billancourt": "Île-de-France",
    "roissy-en-france": "Île-de-France",
    "le plessis-trévise": "Île-de-France",
    "bondoufle": "Île-de-France",
    "la courneuve": "Île-de-France",
    "neuilly-sur-marne": "Île-de-France",
    "palaiseau": "Île-de-France",

    "lyon": "Auvergne-Rhône-Alpes",
    "greater lyon area": "Auvergne-Rhône-Alpes",
    "villeurbanne": "Auvergne-Rhône-Alpes",
    "st.-fons": "Auvergne-Rhône-Alpes",
    "neyron": "Auvergne-Rhône-Alpes",
    "ouges": "Bourgogne-Franche-Comté",
    "valence": "Auvergne-Rhône-Alpes",
    "ambilly": "Auvergne-Rhône-Alpes",

    "strasbourg": "Grand Est",
    "greater strasbourg metropolitan area": "Grand Est",
    "colmar": "Grand Est",
    "gérardmer": "Grand Est",
    "illkirch-graffenstaden": "Grand Est",
    "marlenheim": "Grand Est",
    "monswiller": "Grand Est",
    "molsheim": "Grand Est",
    "erstein": "Grand Est",
    "lingolsheim": "Grand Est",
    "nancy": "Grand Est",
    "greater nancy area": "Grand Est",
    "reims": "Grand Est",
    "troyes": "Grand Est",
    "laxou": "Grand Est",

    "bordeaux": "Nouvelle-Aquitaine",
    "greater bordeaux metropolitan area": "Nouvelle-Aquitaine",
    "lormont": "Nouvelle-Aquitaine",
    "blanquefort": "Nouvelle-Aquitaine",
    "villenave-d’ornon": "Nouvelle-Aquitaine",

    "toulouse": "Occitanie",
    "greater toulouse metropolitan area": "Occitanie",
    "castelnau-le-lez": "Occitanie",
    "rodez": "Occitanie",
    "occitanie": "Occitanie",

    "marseille": "Provence-Alpes-Côte d'Azur",
    "nice": "Provence-Alpes-Côte d'Azur",
    "aix-en-provence": "Provence-Alpes-Côte d'Azur",
    "la garde": "Provence-Alpes-Côte d'Azur",
    "briançon": "Provence-Alpes-Côte d'Azur",

    "lille": "Hauts-de-France",
    "greater lille metropolitan area": "Hauts-de-France",
    "compiègne": "Hauts-de-France",
    "grandvilliers": "Hauts-de-France",
    "amiens": "Hauts-de-France",

    "rennes": "Bretagne",
    "greater rennes metropolitan area": "Bretagne",

    "angers": "Pays de la Loire",
    "le mans": "Pays de la Loire",
    "beaupréau-en-mauges": "Pays de la Loire",
    "la chapelle-sur-erdre": "Pays de la Loire",

    "tours": "Centre-Val de Loire",
    "chatillon": "Île-de-France",

    "dijon": "Bourgogne-Franche-Comté",
    "fontaine-lès-dijon": "Bourgogne-Franche-Comté",
    "chenôve": "Bourgogne-Franche-Comté",
    "lons-le-saunier": "Bourgogne-Franche-Comté",

    "annecy": "Auvergne-Rhône-Alpes",
    "haute-savoie": "Auvergne-Rhône-Alpes",
    
    "bayonne": "Nouvelle-Aquitaine",
    "bayeux": "Normandie",
    "granville": "Normandie",
    "rouen": "Normandie",
    "la rochelle": "Nouvelle-Aquitaine",

    "amsterdam": "Pays-Bas",  # cas spéciaux
    "monde": "International"
}


def clean_location(loc: str) -> str:
    return loc.lower().split("(")[0].strip()


def get_region(location: str) -> str:
    cleaned = clean_location(location)
    return location_to_region.get(cleaned, "Autre")


# === Interface Streamlit ===
st.title("🗺️ Attribution automatique des régions par localisation")

uploaded_file = st.file_uploader("Upload ton fichier Excel avec les localisations", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    st.write("Aperçu du fichier :")
    st.dataframe(df.head())

    column = st.selectbox("Choisis la colonne contenant la localisation", df.columns)

    if st.button("Attribuer les régions"):
        df["Région"] = df[column].astype(str).apply(get_region)
        st.success("✅ Régions attribuées !")
        st.dataframe(df.head())

        # Téléchargement
        @st.cache_data
        def convert_df(df):
            return df.to_excel(index=False, engine='openpyxl')

        st.download_button("📥 Télécharger le fichier avec régions", convert_df(df), file_name="données_avec_régions.xlsx")

