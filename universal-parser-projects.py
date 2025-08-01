import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Universal Project Parser with Structure Detection", layout="wide")
st.title("🧠 Universal Project Parser — Structure par exemple")

st.markdown("""
**Mode d’emploi :**

1. Indique le nombre de catégories d’informations à extraire.  
2. Pour chaque catégorie, donne son nom et un exemple précis extrait d’une fiche complète.  
3. Colle ensuite **une fiche complète EXEMPLE**, contenant toutes les infos dans l’ordre (non découpée).  
4. Colle le gros bloc brut contenant toutes les fiches projets à parser.  
5. Le tableau sera généré et téléchargeable.  
""")

# Step 1 - Saisie catégories et exemples
category_count = st.number_input("Nombre de catégories à extraire", min_value=1, max_value=10, value=3, step=1)

categories = []
examples = []
for i in range(category_count):
    c1, c2 = st.columns([1,2])
    with c1:
        cat = st.text_input(f"Nom catégorie #{i+1}", key=f"cat_{i}")
    with c2:
        ex = st.text_input(f"Exemple pour '{cat or f'catégorie {i+1}'}'", key=f"ex_{i}")
    categories.append(cat.strip() if cat else "")
    examples.append(ex.strip() if ex else "")

if not all(categories) or not all(examples):
    st.warning("Merci de remplir tous les noms et exemples de catégories pour continuer.")
    st.stop()

# Step 2 - Exemple complet non découpé
st.subheader("2. Colle ici UNE fiche projet complète EXEMPLE (texte brut non découpé) correspondant aux exemples donnés ci-dessus")
example_full_text = st.text_area("Fiche exemple complète (ex : toutes les infos dans l’ordre)", height=150)

if not example_full_text.strip():
    st.warning("Merci de coller une fiche projet exemple complète.")
    st.stop()

# Step 3 - Bloc complet à parser
st.subheader("3. Colle ici le texte complet contenant TOUTES les fiches projets à parser (brut, non découpé)")
all_projects_text = st.text_area("Bloc complet de fiches projets", height=400)

if not all_projects_text.strip():
    st.warning("Merci de coller le bloc complet à parser.")
    st.stop()

# Fonction pour détecter la structure : on trouve les positions des exemples dans la fiche exemple complète
def detect_structure(full_text, examples):
    positions = []
    lower_text = full_text.lower()
    for ex in examples:
        ex_lower = ex.lower()
        pos = lower_text.find(ex_lower)
        if pos == -1:
            return None  # Exemple non trouvé, on ne peut pas détecter la structure
        positions.append((pos, ex))
    # Trier par position croissante
    positions.sort(key=lambda x: x[0])
    # On récupère la structure : ordre et découpage par positions successives
    return positions

# Fonction pour découper un bloc complet selon la structure détectée
def parse_block(block_text, structure):
    fields = []
    for i in range(len(structure)):
        start_pos = structure[i][0]
        end_pos = structure[i+1][0] if i+1 < len(structure) else len(block_text)
        field_text = block_text[start_pos:end_pos].strip()
        # Nettoyer le field_text en enlevant l'exemple exact (optionnel)
        example_text = structure[i][1]
        # On garde le texte brut ici (pas d'enlèvement automatique)
        fields.append(field_text)
    return fields

# On détecte la structure sur la fiche exemple complète
structure = detect_structure(example_full_text, examples)

if structure is None:
    st.error("Un ou plusieurs exemples ne sont pas trouvés dans la fiche exemple complète. Vérifie les correspondances.")
    st.stop()

st.markdown(f"**Structure détectée (ordre des champs) :** {[categories[examples.index(ex)] for _, ex in structure]}")

# On découpe le gros bloc complet en fiches selon la répétition du premier exemple
first_example_text = examples[0].lower()
# Pour découper gros bloc, on va chercher la position des occurrences du premier exemple
def split_projects(text, first_example):
    positions = []
    lower_text = text.lower()
    start = 0
    while True:
        pos = lower_text.find(first_example, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    # découper le texte en tranches entre ces positions
    projects = []
    for i in range(len(positions)):
        start_pos = positions[i]
        end_pos = positions[i+1] if i+1 < len(positions) else len(text)
        projects.append(text[start_pos:end_pos].strip())
    return projects

projects = split_projects(all_projects_text, first_example_text)

# Parser chaque projet selon la structure détectée
rows = []
for proj in projects:
    parsed = parse_block(proj, structure)
    if len(parsed) == len(categories):
        rows.append(parsed)
    else:
        # si nombre de champs différent, on complète par vide
        parsed.extend([""]*(len(categories)-len(parsed)))
        rows.append(parsed)

# Construction DataFrame
df = pd.DataFrame(rows, columns=categories)

st.subheader("Tableau extrait")
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
