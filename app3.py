import streamlit as st
import pandas as pd
import io

st.title("📄 Parser multi-pages - Offres Station F → Excel")

# Initialisation des variables de session
if "total_pages_expected" not in st.session_state:
    st.session_state["total_pages_expected"] = 1

if "pages_added" not in st.session_state:
    st.session_state["pages_added"] = 0

if "all_pages" not in st.session_state:
    st.session_state["all_pages"] = []

# Saisie du nombre de pages attendues (modifiable seulement si aucune page n'a été ajoutée)
if st.session_state["pages_added"] == 0:
    st.session_state["total_pages_expected"] = st.number_input(
        "Combien de pages vas-tu coller ?", min_value=1, max_value=100, value=5, step=1
    )
else:
    st.info(f"Nombre de pages prévues : {st.session_state['total_pages_expected']}")

# Affichage de la barre de progression
progress = st.progress(st.session_state["pages_added"] / st.session_state["total_pages_expected"])
st.caption(f"{st.session_state['pages_added']} / {st.session_state['total_pages_expected']} pages ajoutées")

# Zone de texte pour coller une page
raw_text = st.text_area("📋 Colle ici le texte brut d'une page :", height=300)

def parse_three_line_jobs(text):
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    jobs = []
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            contrat_titre = lines[i]
            startup = lines[i+1]
            type_poste = lines[i+2]

            if " - " in contrat_titre:
                contrat, titre = contrat_titre.split(" - ", 1)
            else:
                contrat = ""
                titre = contrat_titre

            jobs.append({
                "Type de contrat": contrat.strip(),
                "Titre du poste": titre.strip(),
                "Startup": startup,
                "Type de poste": type_poste
            })
    return jobs

# Ajout de la page
if st.session_state["pages_added"] < st.session_state["total_pages_expected"]:
    if st.button("📄 Ajouter cette page"):
        if raw_text.strip():
            parsed = parse_three_line_jobs(raw_text)
            st.session_state["all_pages"].extend(parsed)
            st.session_state["pages_added"] += 1
            st.success(f"{len(parsed)} offres ajoutées. Total cumulé : {len(st.session_state['all_pages'])}")
            st.experimental_rerun()  # Pour rafraîchir la barre + vider zone
else:
    st.warning("✅ Tu as déjà ajouté toutes les pages prévues.")

# Affichage cumulatif
if st.session_state["all_pages"]:
    df_all = pd.DataFrame(st.session_state["all_pages"])
    st.subheader("📊 Toutes les offres cumulées")
    st.dataframe(df_all)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_all.to_excel(writer, index=False, sheet_name='Offres')

    st.download_button(
        label="📥 Télécharger Excel",
        data=buffer.getvalue(),
        file_name="offres_stationf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Réinitialiser tout
if st.button("🔄 Réinitialiser tout"):
    st.session_state["all_pages"] = []
    st.session_state["pages_added"] = 0
    st.session_state["total_pages_expected"] = 1
    st.success("Tout a été réinitialisé.")
