import streamlit as st
import pandas as pd
import io

st.title("Parseur Offres - Multi-pages")

# --- INIT STATE ---
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "current_page" not in st.session_state:
    st.session_state.current_page = 1
if "raw_texts" not in st.session_state:
    st.session_state.raw_texts = []

# --- ENTRÉE DU NOMBRE DE PAGES ---
if st.session_state.current_page == 1:
    st.session_state.num_pages = st.number_input("Nombre total de pages :", min_value=1, max_value=50, value=1, step=1)

st.progress((st.session_state.current_page - 1) / st.session_state.num_pages)
st.markdown(f"**Page {st.session_state.current_page} sur {st.session_state.num_pages}**")

# --- TEXT INPUT ---
text_input = st.text_area(f"Copiez-collez ici le contenu de la page {st.session_state.current_page} :", height=300)

# --- BOUTON PAGE SUIVANTE ---
if st.button("Page suivante"):
    if text_input.strip() == "":
        st.warning("Veuillez coller du texte avant de passer à la page suivante.")
    else:
        st.session_state.raw_texts.append(text_input.strip())
        if st.session_state.current_page < st.session_state.num_pages:
            st.session_state.current_page += 1
        else:
            st.success("Toutes les pages ont été remplies !")

# --- PARSING ---
def parse_text(text):
    lines = [line.strip() for line in text.split("\n") if line.strip() != ""]
    jobs = []
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            contrat_poste = lines[i]
            startup = lines[i + 1]
            type_poste = lines[i + 2]
            jobs.append((contrat_poste, startup, type_poste))
    return jobs

# --- AFFICHAGE FINAL + TÉLÉCHARGEMENT ---
if st.session_state.current_page > st.session_state.num_pages:
    st.subheader("Résultat final")

    all_jobs = []
    for page in st.session_state.raw_texts:
        all_jobs.extend(parse_text(page))

    df = pd.DataFrame(all_jobs, columns=["Contrat + Poste", "Startup", "Type"])

    st.dataframe(df)

    # Téléchargement en .xlsx
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Offres")
    st.download_button("📥 Télécharger en .xlsx", output.getvalue(), file_name="offres_stationf.xlsx")
