
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
st.markdown("Reproduisez la séquence des catégories entre crochets, dans l’ordre, avec la mise en forme exacte, par ex :\n\n```\n[Année]\n[Startup]\n\n[taille équipe]\n```")
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
# Le modèle contient des tags [Categorie], on va les remplacer par des groupes regex capturant les valeurs
# On capture tout ce qui est entre les tags, en mode "non gourmand" (.*?)
# Exemple : modèle "[Année]\n[Startup]" => regex qui capture un groupe après [Année], puis un groupe après [Startup]

def build_regex_from_model(model, categories):
    # On va remplacer chaque tag [Catégorie] par un groupe capturant (.+?) qui capture au moins un caractère (lazy)
    # Entre les tags, on garde la mise en forme exacte (retours ligne, espaces)
    regex = escape_special_regex_chars(model)
    for cat in categories:
        regex = regex.replace(f"[{cat}]", f"(?P<{cat}>.+?)")
    # Ajouter re.DOTALL pour que '.' capture les sauts de ligne
    return regex

regex_pattern = build_regex_from_model(model_text, categories)

try:
    compiled_re = re.compile(regex_pattern, re.DOTALL)
except Exception as e:
    st.error(f"Erreur dans la compilation de la regex : {e}")
    st.stop()

# Trouver toutes les correspondances dans le texte complet
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
