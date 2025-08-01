import streamlit as st
import re
import pandas as pd

st.title("Parser de contenu startup")

# Zone de texte pour coller le contenu
input_text = st.text_area("Colle ici ton contenu (Nom startup / Tour / Pitch)", height=300)

def parse_startups(text):
    # On suppose que chaque startup commence par une ligne de nom,
    # suivie d'une ligne tour de levée, puis le pitch (qui peut faire plusieurs lignes)
    # jusqu'à la prochaine startup.

    # Pour cela, on peut chercher toutes les occurences de :
    # Nom startup : une ligne qui commence par un mot avec majuscule, sans chiffre (simplifié)
    # Tour de levée : ligne contenant 'Seed', 'Series A', 'Series B', etc.
    # Puis le pitch jusqu'à la prochaine startup

    # On va utiliser une regex qui capture les trois blocs, en mode multiline et dotall (pour inclure retours à la ligne)

    pattern = re.compile(
        r"(?P<name>^[A-Z][^\n]+)\n"   # Nom startup : ligne commençant par majuscule
        r"(?P<round>(Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)[^\n]*)\n"  # Tour de levée (approximatif)
        r"(?P<pitch>.*?)(?=\n[A-Z][^\n]+\n(?:Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)|\Z)",  # pitch jusqu'à la prochaine startup ou fin de texte
        re.MULTILINE | re.DOTALL
    )

    results = []
    for match in pattern.finditer(text):
        name = match.group("name").strip()
        round_ = match.group("round").strip()
        pitch = match.group("pitch").strip().replace('\n', ' ')
        results.append({"Startup": name, "Tour de levée": round_, "Pitch": pitch})

    return results

if input_text:
    startups = parse_startups(input_text)
    if startups:
        df = pd.DataFrame(startups)
        st.dataframe(df)
    else:
        st.warning("Aucun startup détecté dans le texte collé. Vérifie le format.")
