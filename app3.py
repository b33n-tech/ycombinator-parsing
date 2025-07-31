import streamlit as st
import pandas as pd
import io

st.title("📄 Parser multi-pages - Offres Station F → Excel")

# Initialiser les sessions
if "all_pages" not in st.session_state:
    st.session_state["all_pages"] = []

if "text_input_page_tmp" not in st.session_state:
    st.session_state["text_input_page_tmp"] = ""

st.markdown("""
Colle ici le contenu **d'une seule page** du jobboard Station F (format 3 lignes par offre)  
➡️ Clique sur **“Ajouter cette page”**  
🔁 Répète autant de fois que nécessaire  
📥 Puis clique sur **“Télécharger Excel”** quand tu as fini
""")

# Affichage de la zone de texte
text_input = st.text_area("📋 Colle ici le texte brut d'une page :", 
                          height=300, 
                          key="text_input_page_tmp")

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

# Bouton d'ajout
if st.button("📄 Ajouter cette page"):
    if st.session_state["text_input_page_tmp"].strip():
        parsed = parse_three_line_jobs(st.session_state["text_input_page_tmp"])
        st.session_state["all_pages"].extend(parsed)
        st.success(f"{len(parsed)} offres ajoutées. Total : {len(st.session_state['all_pages'])}")

        # Forcer le champ à se vider (en remettant à blanc la session)
        st.session_state["text_input_page_tmp"] = ""

# Affichage des données cumulées
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

if st.button("🔄 Réinitialiser toutes les pages"):
    st.session_state["all_pages"] = []
    st.success("Toutes les données ont été réinitialisées.")
