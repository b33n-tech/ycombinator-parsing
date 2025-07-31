import streamlit as st
import re

st.title("Parseur Offres - Multi-pages")

# Nombre de pages à copier/coller
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "raw_texts" not in st.session_state:
    st.session_state.raw_texts = []

# Entrée du nombre de pages (modifiable uniquement si on n'a pas commencé)
if st.session_state.current_page == 1:
    st.session_state.num_pages = st.number_input("Nombre total de pages :", min_value=1, max_value=50, value=1, step=1)

st.progress((st.session_state.current_page - 1) / st.session_state.num_pages)

st.markdown(f"**Page {st.session_state.current_page} sur {st.session_state.num_pages}**")

# Zone de texte pour la page courante
text_input = st.text_area(f"Copiez-collez ici le contenu de la page {st.session_state.current_page} :", height=300)

# Bouton pour passer à la page suivante
if st.button("Page suivante"):
    if text_input.strip() == "":
        st.warning("Veuillez coller du texte avant de passer à la page suivante.")
    else:
        st.session_state.raw_texts.append(text_input.strip())
        if st.session_state.current_page < st.session_state.num_pages:
            st.session_state.current_page += 1
        else:
            st.success("Toutes les pages ont été remplies !")

# Lorsque toutes les pages ont été remplies
if st.session_state.current_page > st.session_state.num_pages:
    st.subheader("Résultat final")

    def parse_text(text):
        lines = text.split("\n")
        jobs = []
        for i in range(0, len(lines), 3):
            if i + 2 < len(lines):
                contrat_poste = lines[i].strip()
                startup = lines[i + 1].strip()
                type_poste = lines[i + 2].strip()
                jobs.append((contrat_poste, startup, type_poste))
        return jobs

    all_jobs = []
    for page in st.session_state.raw_texts:
        all_jobs.extend(parse_text(page))

    for job in all_jobs:
        st.write(f"**Poste :** {job[0]}  \n**Startup :** {job[1]}  \n**Type :** {job[2]}")
