import streamlit as st

# Dictionnaire élargi des tags avec mots-clés
tags_keywords = {
    "Management": [
        "responsable", "chef de projet", "chief of staff", "coordinateur", "bras droit", "directeur", "manager", "program manager", "project manager", "pm", "gestion", "organisational development", "responsable de programme", "référent pédagogique", "chef·fe de service", "chef de projets", "management", "operation", "product owner", "strategy", "operation"
    ],
    "Commercial / Vente": [
        "commercial", "business developer", "développement commercial", "affaires", "vente", "biz dev", "partenariats", "business development", "conseiller", "chargé d'affaires", "responsable commercial", "price manager", "development & partnership manager", "business manager", "sales", "développement", "chargé de développement", "charge d'affaires"
    ],
    "Marketing / Communication": [
        "communication", "marketing", "fidélisation", "événementiel", "digital", "rp", "brand", "contenu", "promotion", "chargé de communication", "chargé(e) de projets groupes", "chargé(e) de promotion", "responsable communication", "chargé de projets junior commercial et marketing", "chargé de développement de partenariats et de communication"
    ],
    "Support / Administration": [
        "assistant", "administration", "insertion", "admissions", "gestion", "support", "ressources humaines", "rh", "administratif", "coordination", "chargé d'accompagnement", "chargé de mission", "assistant(e) direction", "assistant administratif", "assistant chef de projet", "assistant(e) direction", "chargé(e) de scolarité", "chargé(e) de service client", "chargé(e) d’administration"
    ],
    "Technique / Ingénierie": [
        "consultant", "ingénieur", "technique", "r&d", "développement", "low-tech", "data", "analyste", "innovation", "digital & ia", "product owner", "junior data migration", "consultant en gestion", "chef de projet digital", "chef de projet data", "chef de projet opérations", "chef de projets programme", "consultant recrutement"
    ],
    "Création / Design": [
        "design", "création", "animateur", "créatif", "rédaction", "ux/ui", "contenu", "animation", "chargé d’animation", "animateur·trice", "chargé de projets groupes & événementiel", "animateur réseau"
    ]
}

def find_tags(title):
    title_low = title.lower()
    found_tags = set()
    for tag, keywords in tags_keywords.items():
        for kw in keywords:
            if kw in title_low:
                found_tags.add(tag)
    if not found_tags:
        found_tags.add("Autre")
    return list(found_tags)

st.title("Taggage automatique des intitulés de postes")

st.write("Entrez une liste de titres de postes, un par ligne :")
input_text = st.text_area("", height=400)

if input_text:
    titles = [line.strip() for line in input_text.split("\n") if line.strip()]
    results = []
    for t in titles:
        tags = find_tags(t)
        results.append((t, ", ".join(tags)))

    st.write("### Résultats :")
    for title, tag_str in results:
        st.write(f"**{title}** → {tag_str}")
