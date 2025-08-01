import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="Parser par Modèle de Séquence", layout="wide")
st.title("Parser universel par Modèle de Séquence")

st.markdown("""
## Mode d'emploi

1. Indiquez les catégories que vous souhaitez extraire (ex : Année, Startup, Taille équipe)  
2. Dans la zone \"Modèle de fiche projet\", copiez la séquence des catégories dans l’ordre, en respectant la mise en forme exacte (retours à la ligne, espacements, etc). Par exemple :

[Année]
[Startup]

[taille équipe]

3. Collez ensuite le texte complet avec toutes les fiches projet à parser (bloc brut, plusieurs fiches à la suite).  
4. Lancez le parsing et téléchargez le tableau généré.
""")

# --- Step 1 : catégories ---
category_count = st.number_input("Nombre de catégories à extraire", min_value=1, max_value=10, value=3, step=1)
categories = []
for i in range(category_count):
    cat = st.text_input(f"Nom catégorie #{i+1}", key=f"cat_{i}")
    categories.append(cat.strip() if cat else "")
if not all(categories):
    st.warning("Merci de remplir tous les noms de catégories.")
    st.stop()

# --- Step 2 : modèle de fiche projet (avec les tags entre crochets) ---
st.subheader("2. Modèle de fiche projet")
st.markdown("Reproduisez la séquence des catégories entre crochets, dans l’ordre, avec la mise en forme exacte, par ex :\n\n[Année]\n[Startup]\n\n[taille équipe]\n")
model_text = st.text_area("Modèle de fiche projet (avec les catégories entre crochets)", height=200)
if not model_text.strip():
    st.warning("Merci de saisir le modèle de fiche projet.")
    st.stop()

# Vérifier que tous les tags catégories sont bien présents dans le modèle
missing_cats = [c for c in categories if f"[{c}]" not in model_text]
if missing_cats:
    st.error(f"Les catégories suivantes ne sont pas présentes dans le modèle avec les crochets [] : {missing_cats}")
    st.stop()

# --- Step 3 : texte complet à parser ---
st.subheader("3. Texte complet avec toutes les fiches projet")
full_text = st.text_area("Collez ici le texte brut contenant toutes les fiches projets", height=400)
if not full_text.strip():
    st.warning("Merci de coller le texte complet à parser.")
    st.stop()

# --- Parsing ---

def escape_special_regex_chars(text):
    return re.escape(text).replace("\\[", "[").replace("\\]", "]")

# Construire une regex à partir du modèle
def build_regex_from_model(model, categories):
    regex = escape_special_regex_chars(model)
    for cat in categories:
        regex = regex.replace(f"[{cat}]", f"(?P<{cat}>.+?)")
    return regex

regex_pattern = build_regex_from_model(model_text, categories)

try:
    compiled_re = re.compile(regex_pattern, re.DOTALL)
except Exception as e:
    st.error(f"Erreur dans la compilation de la regex : {e}")
    st.stop()

matches = list(compiled_re.finditer(full_text))

if not matches:
    st.warning("Aucune fiche projet ne correspond au modèle dans le texte complet.")
    st.stop()

rows = []
for m in matches:
    row = {cat: m.group(cat).strip() for cat in categories}
    rows.append(row)

df = pd.DataFrame(rows)

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
