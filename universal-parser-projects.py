import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.title("🧠 Universal Project Parser — Version guidée")
st.markdown("Créez votre propre schéma de parsing en fournissant les catégories et des exemples pour chacune.")

st.header("🛠️ Étape 1 — Définir les catégories")

num_fields = st.number_input("Combien de types d'information voulez-vous extraire ?", min_value=1, max_value=10, value=3)

field_configs = []

with st.form("field_definition_form"):
    for i in range(num_fields):
        st.subheader(f"Catégorie #{i+1}")
        name = st.text_input(f"Nom de la catégorie {i+1}", key=f"name_{i}")
        ex1 = st.text_input(f"Exemple 1", key=f"ex1_{i}")
        ex2 = st.text_input(f"Exemple 2", key=f"ex2_{i}")
        ex3 = st.text_input(f"Exemple 3", key=f"ex3_{i}")
        field_configs.append({"name": name, "examples": [ex1, ex2, ex3]})

    submitted = st.form_submit_button("✅ Confirmer les catégories")

# Fonction de détection par similarité naïve (peut être améliorée avec NLP plus tard)
def find_matching_field(line, field_configs):
    for config in field_configs:
        for example in config["examples"]:
            if example and example.lower() in line.lower():
                return config["name"]
    return None

if submitted:
    st.success("Catégories enregistrées. Passez à l'étape suivante.")

    st.header("📋 Étape 2 — Coller le texte à parser")
    raw_text = st.text_area("Texte à analyser", height=400)

    if st.button("🚀 Lancer le parsing") and raw_text:
        lines = [l.strip() for l in raw_text.strip().split("\n") if l.strip()]
        parsed_rows = []
        current_row = {config["name"]: "" for config in field_configs}
        used_fields = set()

        for line in lines:
            matched_field = find_matching_field(line, field_configs)
            if matched_field:
                if matched_field in used_fields:
                    parsed_rows.append(current_row)
                    current_row = {config["name"]: "" for config in field_configs}
                    used_fields = set()
                current_row[matched_field] = line
                used_fields.add(matched_field)

        if any(v != "" for v in current_row.values()):
            parsed_rows.append(current_row)

        if parsed_rows:
            df = pd.DataFrame(parsed_rows)
            st.success(f"✅ {len(df)} entrées détectées.")
            st.dataframe(df, use_container_width=True)

            def convert_df_to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Projets')
                return output.getvalue()

            excel_data = convert_df_to_excel(df)
            st.download_button(
                label="📥 Télécharger en Excel",
                data=excel_data,
                file_name="projets_parsés.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Aucune donnée identifiable à parser. Veuillez ajuster vos exemples ou votre texte.")
