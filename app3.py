import streamlit as st
import pandas as pd
import io

st.title("📄 Parser multi-pages - Offres Station F → Excel")

# Initialiser la session si elle n’existe pas
if "all_pages" not in st.session_state:
    st.session_state["all_pages"] = []

st.markdown("""
Colle ici le contenu **d'une seule page** du jobboard Station F (format 3 lignes par offre)  
➡️ Clique sur **“Ajouter cette page”**  
🔁 Répète autant de fois que nécessaire  
📥 Puis clique sur **“Télécharger Excel”** quand tu as fini
""")

raw_text = st.text_area("📋 Colle ici le texte brut d'une page :", height=300)

add_page = st.button("📄 Ajouter cette page")

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

# Ajouter la page à la session
if add_page and raw_text.strip():
    parsed = parse_three_line_jobs(raw_text)
    st.session_state.all_pages.extend(parsed)
    st.success(f"{len(parsed)} offres ajoutées. Total : {len(st.session_state.all_pages)}")
    st.experimental_rerun()  # Pour vider la zone de texte après ajout

# Affichage des résultats cumulatifs
if st.session_state.all_pages:
    df_all = pd.DataFrame(st.session_state.all_pages)
    st.subheader("📊 Toutes les offres cumulées")
    st.dataframe(df_all)

    # Bouton pour exporter en Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_all.to_excel(writer, index=False, sheet_name='Offres')

    st.download_button(
        label="📥 Télécharger Excel",
        data=buffer.getvalue(),
        file_name="offres_stationf.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Option : Réinitialiser
if st.button("🔄 Réinitialiser toutes les pages"):
    st.session_state.all_pages = []
    st.success("Toutes les données ont été réinitialisées.")
