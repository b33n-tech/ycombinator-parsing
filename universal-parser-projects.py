import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Parser basé sur séquence ordonnée", layout="wide")
st.title("🧩 Parser universel basé sur séquence ordonnée")

st.markdown("""
### Mode d’emploi :

1. Indique les noms des catégories d’informations, dans l’ordre où elles apparaissent dans un projet, séparés par une virgule (ex : Nom, Date, Tags, Pitch).  
2. Colle la séquence brute complète d’un projet unique (texte où apparaissent ces infos dans cet ordre, non découpé).  
3. Colle le bloc complet contenant **plusieurs projets** similaires collés bout à bout dans le même ordre.  
4. Clique sur **Parser**.  
5. Le tableau s’affiche et tu peux télécharger le fichier Excel.  
""")

# 1. Saisie catégories (séquence)
categories_raw = st.text_input("1. Indique les catégories séparées par une virgule (ex : Nom, Date, Tags, Pitch)")

if not categories_raw.strip():
    st.warning("Merci d'indiquer les catégories pour continuer.")
    st.stop()

categories = [c.strip() for c in categories_raw.split(",") if c.strip()]
if len(categories) < 1:
    st.warning("Merci d'indiquer au moins une catégorie valide.")
    st.stop()

# 2. Séquence brute d'un projet unique
example_project = st.text_area("2. Colle ici la séquence brute complète d’un projet unique (non découpée)", height=150)
if not example_project.strip():
    st.warning("Merci de coller la séquence brute d'un projet.")
    st.stop()

# 3. Bloc complet à parser
all_projects_text = st.text_area("3. Colle ici le texte complet contenant toutes les fiches projets (non découpé)", height=400)
if not all_projects_text.strip():
    st.warning("Merci de coller le texte complet à parser.")
    st.stop()

def find_positions(sequence_text, categories):
    """
    Trouve dans sequence_text la position d'apparition dans l'ordre des catégories.
    Renvoie une liste de tuples (cat, start_pos)
    """
    lower_text = sequence_text.lower()
    positions = []
    current_pos = 0
    for cat in categories:
        # Chercher l'apparition suivante de la catégorie en ignorant la casse
        pos = lower_text.find(cat.lower(), current_pos)
        if pos == -1:
            # Si on ne trouve pas la catégorie, essaye de chercher un mot clé ou place une position fictive
            # Ici on peut juste stopper l'analyse
            return None
        positions.append((cat, pos))
        current_pos = pos + 1
    return positions

# Ici on va chercher non pas les noms des catégories (qui sont juste des labels),
# mais on va supposer que dans la séquence brute, la séquence des catégories est marquée
# par des textes identifiables (on peut aussi partir sur un découpage par l'ordre des catégories et découpage par position)

# Puisque le user colle une séquence brute, on va utiliser la longueur moyenne pour découper
# plutôt que chercher les mots catégorie, on découpe en parts égales selon la séquence

def parse_project_block(block_text, categories):
    """
    Coupe block_text en len(categories) parts à peu près égales, retourne la liste des strings
    """
    length = len(block_text)
    step = length // len(categories)
    parts = []
    for i in range(len(categories)):
        start = i*step
        end = (i+1)*step if i < len(categories)-1 else length
        part = block_text[start:end].strip()
        parts.append(part)
    return parts

def split_projects(text, example_proj):
    """
    Recherche la position des occurrences du projet exemple dans le texte complet.
    Coupe le texte en tranches entre ces occurrences.
    """
    lower_text = text.lower()
    example_lower = example_proj.lower()
    positions = []
    start = 0
    while True:
        pos = lower_text.find(example_lower, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    projects = []
    for i in range(len(positions)):
        start_pos = positions[i]
        end_pos = positions[i+1] if i+1 < len(positions) else len(text)
        projects.append(text[start_pos:end_pos].strip())
    return projects

if st.button("Parser"):
    # On découpe le texte complet en projets
    projects = split_projects(all_projects_text, example_project)

    if len(projects) == 0:
        st.error("Impossible de trouver des occurrences du projet exemple dans le texte complet.")
        st.stop()

    rows = []
    for p in projects:
        # On découpe chaque projet en N parties égales selon les catégories
        parsed = parse_project_block(p, categories)
        if len(parsed) == len(categories):
            rows.append(parsed)
        else:
            parsed.extend([""]*(len(categories)-len(parsed)))
            rows.append(parsed)

    df = pd.DataFrame(rows, columns=categories)
    st.subheader("Résultat du parsing")
    st.dataframe(df, use_container_width=True)

    # Export XLSX
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Projets')
    processed_data = output.getvalue()

    st.download_button(
        label="📥 Télécharger le fichier Excel",
        data=processed_data,
        file_name="parsed_projects.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
