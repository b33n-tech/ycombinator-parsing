import streamlit as st
import pandas as pd

# -----------------------
# DICTIONNAIRE DE RÉPARTITION DES VILLES PAR RÉGION
# -----------------------

ville_to_region = {
    # Île-de-France
    "Paris": "Île-de-France",
    "Greater Paris Metropolitan Region": "Île-de-France",
    "Puteaux": "Île-de-France",
    "Neuilly-sur-Marne": "Île-de-France",
    "Paray-Vieille-Poste": "Île-de-France",
    "Noisy-le-Grand": "Île-de-France",
    "Bry-sur-Marne": "Île-de-France",
    "Bondoufle": "Île-de-France",
    "Roissy-en-France": "Île-de-France",
    "Rueil-Malmaison": "Île-de-France",
    "Le Plessis-Trévise": "Île-de-France",
    "Levallois-Perret": "Île-de-France",
    "Versailles": "Île-de-France",
    "Neuilly-sur-Seine": "Île-de-France",
    "La Courneuve": "Île-de-France",
    "Palaiseau": "Île-de-France",

    # Grand Est
    "Strasbourg": "Grand Est",
    "Greater Strasbourg Metropolitan Area": "Grand Est",
    "Nancy": "Grand Est",
    "Greater Nancy Area": "Grand Est",
    "Colmar": "Grand Est",
    "Molsheim": "Grand Est",
    "Erstein": "Grand Est",
    "Gérardmer": "Grand Est",
    "Marlenheim": "Grand Est",
    "Monswiller": "Grand Est",
    "Illkirch-Graffenstaden": "Grand Est",
    "Laxou": "Grand Est",
    "Lingolsheim": "Grand Est",

    # Auvergne-Rhône-Alpes
    "Lyon": "Auvergne-Rhône-Alpes",
    "Greater Lyon Area": "Auvergne-Rhône-Alpes",
    "Villeurbanne": "Auvergne-Rhône-Alpes",
    "St.-Fons": "Auvergne-Rhône-Alpes",
    "Valence": "Auvergne-Rhône-Alpes",
    "Neyron": "Auvergne-Rhône-Alpes",
    "Ambilly": "Auvergne-Rhône-Alpes",
    "Annecy": "Auvergne-Rhône-Alpes",
    "Haute-Savoie": "Auvergne-Rhône-Alpes",
    "Clermont-Ferrand": "Auvergne-Rhône-Alpes",
    "Saint-Didier-sur-Chalaronne": "Auvergne-Rhône-Alpes",
    "Ouges": "Bourgogne-Franche-Comté",
    "Chenôve": "Bourgogne-Franche-Comté",
    "Lons-le-Saunier": "Bourgogne-Franche-Comté",

    # Nouvelle-Aquitaine
    "Bordeaux": "Nouvelle-Aquitaine",
    "Greater Bordeaux Metropolitan Area": "Nouvelle-Aquitaine",
    "Lormont": "Nouvelle-Aquitaine",
    "Blanquefort": "Nouvelle-Aquitaine",
    "Villenave-d’Ornon": "Nouvelle-Aquitaine",

    # Occitanie
    "Toulouse": "Occitanie",
    "Greater Toulouse Metropolitan Area": "Occitanie",
    "Rodez": "Occitanie",
    "Castelnau-le-Lez": "Occitanie",
    "Occitanie, France": "Occitanie",

    # Provence-Alpes-Côte d'Azur
    "Aix-en-Provence": "Provence-Alpes-Côte d'Azur",
    "Marseille": "Provence-Alpes-Côte d'Azur",
    "Nice": "Provence-Alpes-Côte d'Azur",
    "Maritime Alps": "Provence-Alpes-Côte d'Azur",
    "Briançon": "Provence-Alpes-Côte d'Azur",
    "La Garde": "Provence-Alpes-Côte d'Azur",

    # Pays de la Loire
    "La Chapelle-sur-Erdre": "Pays de la Loire",
    "Angers": "Pays de la Loire",
    "Beaupréau-en-Mauges": "Pays de la Loire",
    "Le Mans": "Pays de la Loire",

    # Bretagne
    "Rennes": "Bretagne",
    "Greater Rennes Metropolitan Area": "Bretagne",

    # Normandie
    "Rouen": "Normandie",
    "Granville": "Normandie",
    "Bayeux": "Normandie",

    # Centre-Val de Loire
    "Tours": "Centre-Val de Loire",

    # Hauts-de-France
    "Lille": "Hauts-de-France",
    "Greater Lille Metropolitan Area": "Hauts-de-France",
    "Compiègne": "Hauts-de-France",
    "Grandvilliers": "Hauts-de-France",

    # Bourgogne-Franche-Comté
    "Dijon": "Bourgogne-Franche-Comté",
    
    # Corse
    "Bastia": "Corse",

    # Autres (ou à affiner)
    "Châtillon": "Île-de-France",
    "Grigny": "Île-de-France",
    "Amsterdam Area": "International"
}

# -----------------------
# STREAMLIT APP
# -----------------------

st.title("🗺️ Attribution des régions selon les villes")
st.write("Dépose un fichier Excel avec une colonne de **localisations** (ex: Paris, Lyon, etc.). Le script attribuera la région correspondante.")

uploaded_file = st.file_uploader("📂 Upload Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Détection automatique de la colonne qui contient les localisations
    col_ville = None
    for col in df.columns:
        if df[col].astype(str).str.contains(r'Paris|Lyon|Strasbourg|Toulouse|Bordeaux', case=False).any():
            col_ville = col
            break

    if not col_ville:
        st.error("❌ Impossible de détecter une colonne contenant les noms de villes.")
    else:
        def extraire_ville(v):
            v = str(v).split("(")[0].strip()
            return v.replace("Île-de-France, France", "Île-de-France").replace("Occitanie, France", "Occitanie")

        df['Ville nettoyée'] = df[col_ville].apply(extraire_ville)
        df['Région'] = df['Ville nettoyée'].map(ville_to_region).fillna("À vérifier")

        st.success("✅ Traitement terminé. Aperçu des données :")
        st.dataframe(df.head(15))

        @st.cache_data
        def convert_df(x):
            return x.to_excel(index=False, engine='openpyxl')

        st.download_button(
            label="📥 Télécharger le fichier avec les régions",
            data=convert_df(df),
            file_name="localisations_avec_regions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
