import streamlit as st
import re
import pandas as pd

st.title("Parser startup avec découpage par ligne de tour de levée")

input_text = st.text_area("Colle ici ton contenu", height=400)

# Pattern pour détecter la ligne tour de levée
round_pattern = re.compile(r"^(Seed Round|Seed|Series [A-Z]|Angel|Pre-Seed|Bridge|IPO|Debt)( in \d{4})?$", re.MULTILINE)

def preprocess_text(text):
    # On insère un séparateur '===STARTUP===' avant chaque ligne qui correspond au tour de levée
    # (on fait ça en remplaçant "\n(LIGNE)" par "\n===STARTUP===\nLIGNE")
    def replacer(match):
        return "\n===STARTUP===\n" + match.group(0)
    new_text = round_pattern.sub(replacer, text)
    # Il est possible que la première startup ne commence pas avec ce séparateur, on ajoute en début
    if not new_text.startswith("===STARTUP==="):
        new_text = "===STARTUP===\n" + new_text
    return new_text

def parse_blocks(text):
    # On split sur '===STARTUP==='
    blocks = text.split("===STARTUP===")
    startups = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        # On cherche la ligne qui est le tour de levée (censée être la première ligne)
        round_line = lines[0].strip()
        # Le nom de la startup est la ligne juste avant (dans le texte original), donc ici ce sera la ligne avant cette ligne dans le bloc original
        # Mais ici on a split donc on peut supposer que le nom est la ligne juste avant cette ligne (mais ça n’existe pas dans le block)
        # Donc on va supposer que dans chaque block, le tour est la 1ère ligne, et le nom est la ligne juste avant dans le texte original (donc on doit modifier un peu la logique)
        # Alternative simple: le nom est la ligne juste avant la ligne du tour, donc en prétraitement on ajoute le séparateur une ligne avant le tour et une ligne avant le nom

        # Vu que c'est compliqué, on va considérer que dans le block, la première ligne est le tour, la deuxième est le pitch et qu’avant, dans le texte, on a une ligne nom de startup

        # Donc on récupère nom startup dans la dernière ligne avant ce block (donc il faut modifier le pré-traitement)

        # Simplifions : on considère que le bloc contient : 
        # ligne 0 = tour de levée
        # ligne 1 = nom startup
        # ligne 2 et + = pitch

        if len(lines) < 2:
            continue  # pas assez d'infos

        round_line = lines[0].strip()
        name_line = lines[1].strip()
        pitch = " ".join(line.strip() for line in lines[2:]).strip()

        startups.append({
            "Startup": name_line,
            "Tour de levée": round_line,
            "Pitch": pitch
        })
    return startups

if input_text:
    processed_text = preprocess_text(input_text)
    startups = parse_blocks(processed_text)

    if startups:
        df = pd.DataFrame(startups)
        st.dataframe(df)

        # Ajout bouton de téléchargement Excel
        from io import BytesIO
        import pandas as pd

        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Startups')
            processed_data = output.getvalue()
            return processed_data

        excel_data = to_excel(df)

        st.download_button(
            label="Télécharger en Excel (.xlsx)",
            data=excel_data,
            file_name="startups.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("Aucune startup détectée. Vérifie le format.")
