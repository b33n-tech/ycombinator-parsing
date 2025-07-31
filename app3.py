import streamlit as st
import pandas as pd
import io
import re

st.set_page_config(page_title="Parsing offres Station F", layout="wide")

st.title("📄 Parser les offres à partir de ton copié-collé")

# Initialisation des variables de session
if "all_offers" not in st.session_state:
    st.session_state.all_offers = []
if "page_counter" not in st.session_state:
    st.session_state.page_counter = 0
if "finished" not in st.session_state:
    st.session_state.finished = False
if "total_pages" not in st.session_state:
    st.session_state.total_pages = 3

# Fonction pour parser une page
def parse_page(text):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    offers = []
    i = 0
    while i < len(lines) - 2:
        contrat_poste = lines[i]
        startup = lines[i + 1]
        type_poste = lines[i + 2]
        match = re.match(r"^(CDI|CDD|Stage|Alternance|Freelance|VIE|Internship|Apprentissage|Service civique|Volunteer)\s*-\s*(.*)", contrat_poste)
        if match:
            contrat = match.group(1)
            poste = match.group(2)
            offers.append({
                "Contrat": contrat,
                "Poste": poste,
                "Startup": startup,
                "Type": type_poste
            })
            i += 3
        else:
            i += 1
    return offers

# Choix du nombre de pages
if not st.session_state.finished:
    st.session_state.total_pages = st.slider("Combien de pages vas-tu ajouter au total ?", 1, 20, st.session_state.total_pages)

# Ajout de contenu tant qu'on n'a pas terminé
if not st.session_state.finished and st.session_state.page_counter < st.session_state.total_pages:
    st.markdown(f"### Page {st.session_state.page_counter + 1} / {st.session_state.total_pages}")
    user_input = st.text_area("Colle ici le texte de cette page :", key=f"input_page_{st.session_state.page_counter}")
    if st.button("➕ Ajouter cette page", key=f"add_page_{st.session_state.page_counter}"):
        st.session_state.all_offers.extend(parse_page(user_input))
        st.session_state.page_counter += 1

# Affichage barre de progression
progress = st.session_state.page_counter / st.session_state.total_pages
st.progress(progress)

# Fin d'ajout
if st.session_state.page_counter >= st.session_state.total_pages:
    st.success("🎉 Tu as ajouté toutes les pages prévues.")
    if st.button("✅ Passer à l'étape suivante"):
        st.session_state.finished = True

# Affichage du tableau + téléchargement
if st.session_state.all_offers:
    df = pd.DataFrame(st.session_state.all_offers)
    st.subheader("📊 Résumé des offres collectées")
    st.dataframe(df, use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Offres")
    output.seek(0)

    st.download_button(
        "📥 Télécharger en .xlsx",
        output,
        file_name="offres_stationf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Réinitialisation
st.divider()
if st.button("♻️ Réinitialiser tout"):
    st.session_state.clear()
