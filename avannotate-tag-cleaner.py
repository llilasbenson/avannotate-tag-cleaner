import io
import re
import unicodedata
from collections import Counter

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TSV Entity Cleaner",
    page_icon="🧹",
    layout="wide",
)


# ============================================================
# INTERFACE TRANSLATIONS
# ============================================================

TRANSLATIONS = {
    "English": {
        "app_title": "TSV Entity Cleaner",
        "app_description": (
            "Upload a TSV file containing people, organization, and place-name "
            "columns, together with a TXT file containing approved People, "
            "Organizations, Places, and Modifications lists. The app removes "
            "unapproved values, moves approved values found in the wrong entity "
            "column to the correct column, and applies listed modifications."
        ),
        "language": "Interface language",
        "upload_tsv": "Upload TSV file",
        "upload_txt": "Upload TXT reference list",
        "tsv_help": "Upload a tab-separated values (.tsv) file.",
        "txt_help": (
            "Upload a TXT file with sections for People, Organizations, Places, "
            "and Modifications."
        ),
        "mapping": "TSV column mapping",
        "mapping_help": (
            "Select the TSV column corresponding to each entity category in the TXT file."
        ),
        "people_column": "TSV column for people",
        "organizations_column": "TSV column for organizations",
        "places_column": "TSV column for places",
        "separator": "Separator between multiple values in a TSV cell",
        "comparison_settings": "Comparison settings",
        "case_insensitive": "Ignore capitalization",
        "accent_insensitive": "Ignore accents/diacritics",
        "strip_whitespace": "Ignore extra surrounding whitespace",
        "process": "Clean and reorganize TSV",
        "preview_original": "Original TSV preview",
        "preview_cleaned": "Cleaned TSV preview",
        "reference_summary": "TXT reference-list summary",
        "people": "People",
        "organizations": "Organizations",
        "places": "Places",
        "modifications": "Modifications",
        "results": "Cleaning results",
        "rows": "Rows",
        "values_checked": "Values checked",
        "values_kept": "Values kept",
        "values_removed": "Values removed",
        "values_moved": "Values moved",
        "values_modified": "Values modified",
        "removed_values": "Removed values",
        "moved_values": "Moved values",
        "modified_values": "Modified values",
        "source_column": "Original column",
        "destination_column": "Destination column",
        "original_value": "Original value",
        "new_value": "New value",
        "value": "Value",
        "count": "Count",
        "no_removed": "No values were removed.",
        "no_moved": "No values were moved.",
        "no_modified": "No values were modified.",
        "download": "Download cleaned TSV",
        "download_name": "cleaned.tsv",
        "missing_files": "Upload both a TSV file and a TXT file to continue.",
        "same_columns_error": (
            "The People, Organizations, and Places mappings must use three different TSV columns."
        ),
        "tsv_error": "The TSV file could not be read.",
        "txt_error": "The TXT file could not be read.",
        "success": "The TSV file was cleaned and reorganized successfully.",
        "unrecognized_sections": "Unrecognized TXT section headings",
        "txt_format": "Expected TXT format",
        "txt_format_example": """People
Juan Pérez
María López

Organizations
University of Texas
UNESCO

Places
Mexico
Austin
Texas

Modifications
Méjico -> México
Univ. of Texas -> University of Texas
""",
    },

    "Español": {
        "app_title": "Depurador de entidades en TSV",
        "app_description": (
            "Suba un archivo TSV con columnas de nombres de personas, organizaciones "
            "y lugares, junto con un archivo TXT que contenga listas de Personas, "
            "Organizaciones, Lugares y Modificaciones. La aplicación elimina valores "
            "no autorizados, mueve los valores autorizados que aparecen en la columna "
            "incorrecta a la columna correspondiente y aplica las modificaciones indicadas."
        ),
        "language": "Idioma de la interfaz",
        "upload_tsv": "Subir archivo TSV",
        "upload_txt": "Subir lista de referencia TXT",
        "tsv_help": "Suba un archivo de valores separados por tabulaciones (.tsv).",
        "txt_help": (
            "Suba un archivo TXT con secciones para Personas, Organizaciones, "
            "Lugares y Modificaciones."
        ),
        "mapping": "Correspondencia de columnas TSV",
        "mapping_help": (
            "Seleccione la columna TSV que corresponde a cada categoría del archivo TXT."
        ),
        "people_column": "Columna TSV para personas",
        "organizations_column": "Columna TSV para organizaciones",
        "places_column": "Columna TSV para lugares",
        "separator": "Separador entre varios valores en una celda TSV",
        "comparison_settings": "Configuración de la comparación",
        "case_insensitive": "Ignorar diferencias entre mayúsculas y minúsculas",
        "accent_insensitive": "Ignorar acentos y signos diacríticos",
        "strip_whitespace": "Ignorar espacios adicionales al principio y al final",
        "process": "Depurar y reorganizar TSV",
        "preview_original": "Vista previa del TSV original",
        "preview_cleaned": "Vista previa del TSV depurado",
        "reference_summary": "Resumen de la lista de referencia TXT",
        "people": "Personas",
        "organizations": "Organizaciones",
        "places": "Lugares",
        "modifications": "Modificaciones",
        "results": "Resultados de la depuración",
        "rows": "Filas",
        "values_checked": "Valores revisados",
        "values_kept": "Valores conservados",
        "values_removed": "Valores eliminados",
        "values_moved": "Valores movidos",
        "values_modified": "Valores modificados",
        "removed_values": "Valores eliminados",
        "moved_values": "Valores movidos",
        "modified_values": "Valores modificados",
        "source_column": "Columna original",
        "destination_column": "Columna de destino",
        "original_value": "Valor original",
        "new_value": "Valor nuevo",
        "value": "Valor",
        "count": "Cantidad",
        "no_removed": "No se eliminó ningún valor.",
        "no_moved": "No se movió ningún valor.",
        "no_modified": "No se modificó ningún valor.",
        "download": "Descargar TSV depurado",
        "download_name": "tsv_depurado.tsv",
        "missing_files": "Suba un archivo TSV y un archivo TXT para continuar.",
        "same_columns_error": (
            "Las correspondencias de Personas, Organizaciones y Lugares deben utilizar "
            "tres columnas TSV diferentes."
        ),
        "tsv_error": "No se pudo leer el archivo TSV.",
        "txt_error": "No se pudo leer el archivo TXT.",
        "success": "El archivo TSV se depuró y reorganizó correctamente.",
        "unrecognized_sections": "Encabezados de sección TXT no reconocidos",
        "txt_format": "Formato TXT esperado",
        "txt_format_example": """Personas
Juan Pérez
María López

Organizaciones
University of Texas
UNESCO

Lugares
México
Austin
Texas

Modificaciones
Méjico -> México
Univ. of Texas -> University of Texas
""",
    },

    "Português": {
        "app_title": "Limpador de entidades em TSV",
        "app_description": (
            "Envie um arquivo TSV com colunas de nomes de pessoas, organizações "
            "e lugares, juntamente com um arquivo TXT contendo listas de Pessoas, "
            "Organizações, Lugares e Modificações. O aplicativo remove valores não "
            "autorizados, move valores autorizados encontrados na coluna errada para "
            "a coluna correta e aplica as modificações indicadas."
        ),
        "language": "Idioma da interface",
        "upload_tsv": "Enviar arquivo TSV",
        "upload_txt": "Enviar lista de referência TXT",
        "tsv_help": "Envie um arquivo de valores separados por tabulação (.tsv).",
        "txt_help": (
            "Envie um arquivo TXT com seções para Pessoas, Organizações, "
            "Lugares e Modificações."
        ),
        "mapping": "Mapeamento das colunas TSV",
        "mapping_help": (
            "Selecione a coluna TSV correspondente a cada categoria do arquivo TXT."
        ),
        "people_column": "Coluna TSV para pessoas",
        "organizations_column": "Coluna TSV para organizações",
        "places_column": "Coluna TSV para lugares",
        "separator": "Separador entre vários valores em uma célula TSV",
        "comparison_settings": "Configurações de comparação",
        "case_insensitive": "Ignorar diferenças entre maiúsculas e minúsculas",
        "accent_insensitive": "Ignorar acentos e sinais diacríticos",
        "strip_whitespace": "Ignorar espaços extras no início e no final",
        "process": "Limpar e reorganizar TSV",
        "preview_original": "Visualização do TSV original",
        "preview_cleaned": "Visualização do TSV limpo",
        "reference_summary": "Resumo da lista de referência TXT",
        "people": "Pessoas",
        "organizations": "Organizações",
        "places": "Lugares",
        "modifications": "Modificações",
        "results": "Resultados da limpeza",
        "rows": "Linhas",
        "values_checked": "Valores verificados",
        "values_kept": "Valores mantidos",
        "values_removed": "Valores removidos",
        "values_moved": "Valores movidos",
        "values_modified": "Valores modificados",
        "removed_values": "Valores removidos",
        "moved_values": "Valores movidos",
        "modified_values": "Valores modificados",
        "source_column": "Coluna original",
        "destination_column": "Coluna de destino",
        "original_value": "Valor original",
        "new_value": "Novo valor",
        "value": "Valor",
        "count": "Quantidade",
        "no_removed": "Nenhum valor foi removido.",
        "no_moved": "Nenhum valor foi movido.",
        "no_modified": "Nenhum valor foi modificado.",
        "download": "Baixar TSV limpo",
        "download_name": "tsv_limpo.tsv",
        "missing_files": "Envie um arquivo TSV e um arquivo TXT para continuar.",
        "same_columns_error": (
            "Os mapeamentos de Pessoas, Organizações e Lugares devem usar "
            "três colunas TSV diferentes."
        ),
        "tsv_error": "Não foi possível ler o arquivo TSV.",
        "txt_error": "Não foi possível ler o arquivo TXT.",
        "success": "O arquivo TSV foi limpo e reorganizado com sucesso.",
        "unrecognized_sections": "Cabeçalhos de seção TXT não reconhecidos",
        "txt_format": "Formato TXT esperado",
        "txt_format_example": """Pessoas
Juan Pérez
María López

Organizações
University of Texas
UNESCO

Lugares
México
Austin
Texas

Modificações
Méjico -> México
Univ. of Texas -> University of Texas
""",
    },
}


# ============================================================
# TXT SECTION HEADING ALIASES
# ============================================================

# These aliases allow the TXT section headings themselves to be written
# in English, Spanish, or Portuguese.

SECTION_ALIASES = {
    "people": {
        "people",
        "person",
        "persons",
        "personas",
        "persona",
        "pessoas",
        "pessoa",
        "people names",
        "person names",
        "nombres de personas",
        "nomes de pessoas",
    },

    "organizations": {
        "organizations",
        "organization",
        "organisations",
        "organisation",
        "organizaciones",
        "organización",
        "organizacoes",
        "organizações",
        "organização",
        "organization names",
        "organisation names",
        "nombres de organizaciones",
        "nomes de organizações",
    },

    "places": {
        "places",
        "place",
        "locations",
        "location",
        "lugares",
        "lugar",
        "locales",
        "locais",
        "place names",
        "location names",
        "nombres de lugares",
        "nomes de lugares",
    },

    "modifications": {
        "modifications",
        "modification",
        "changes",
        "corrections",
        "modificaciones",
        "modificación",
        "cambios",
        "correcciones",
        "modificacoes",
        "modificações",
        "modificação",
        "alteracoes",
        "alterações",
        "correcoes",
        "correções",
    },
}


# ============================================================
# FILE READING
# ============================================================

def decode_uploaded_file(uploaded_file):
    """
    Decode an uploaded text file using several common encodings.
    """
    raw_bytes = uploaded_file.getvalue()

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    for encoding in encodings:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue

    raise ValueError("Unable to decode uploaded file.")


def read_tsv(uploaded_file):
    """
    Read the TSV entirely as strings.
    """
    text = decode_uploaded_file(uploaded_file)

    return pd.read_csv(
        io.StringIO(text),
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_value(
    value,
    ignore_case=True,
    ignore_accents=False,
    strip_whitespace=True,
):
    """
    Normalize a value for comparison only.

    The spelling retained in the final TSV comes from either:
    1. the approved TXT list, or
    2. the right-hand side of a modification rule.
    """
    value = str(value)

    if strip_whitespace:
        value = value.strip()

    # Collapse repeated internal whitespace.
    value = re.sub(r"\s+", " ", value)

    if ignore_accents:
        value = "".join(
            character
            for character in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(character)
        )

    if ignore_case:
        value = value.casefold()

    return value


def normalize_heading(value):
    """
    Normalize TXT section headings.
    """
    value = str(value).strip().casefold()

    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )

    value = re.sub(r"[:\-_]+$", "", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# TXT PARSING
# ============================================================

def identify_section_heading(line):
    """
    Return the canonical section name when a line is recognized
    as a TXT section heading.
    """
    normalized_line = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        normalized_aliases = {
            normalize_heading(alias)
            for alias in aliases
        }

        if normalized_line in normalized_aliases:
            return section_name

    return None


def parse_reference_txt(text):
    """
    Parse the TXT file into:

        {
            "people": [...],
            "organizations": [...],
            "places": [...],
            "modifications": [(old, new), ...]
        }

    Expected structure:

        People
        Juan Pérez
        María López

        Organizations
        University of Texas

        Places
        Mexico
        Austin

        Modifications
        Méjico -> México
        Univ. of Texas -> University of Texas
    """
    sections = {
        "people": [],
        "organizations": [],
        "places": [],
        "modifications": [],
    }

    current_section = None
    unrecognized_content = []

    for raw_line in text.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        section_heading = identify_section_heading(line)

        if section_heading:
            current_section = section_heading
            continue

        if current_section is None:
            unrecognized_content.append(line)
            continue

        if current_section == "modifications":

            if "->" not in line:
                # Ignore malformed modification lines.
                continue

            old_value, new_value = line.split("->", 1)

            old_value = old_value.strip()
            new_value = new_value.strip()

            if old_value and new_value:
                sections["modifications"].append(
                    (old_value, new_value)
                )

        else:
            sections[current_section].append(line)

    # Remove exact duplicates while preserving order.
    for section_name in [
        "people",
        "organizations",
        "places",
    ]:
        sections[section_name] = list(
            dict.fromkeys(sections[section_name])
        )

    # Remove duplicate modification pairs while preserving order.
    sections["modifications"] = list(
        dict.fromkeys(sections["modifications"])
    )

    return sections, unrecognized_content


# ============================================================
# CELL PROCESSING
# ============================================================

def split_cell_values(cell, separator):
    """
    Split a TSV entity cell into individual values.
    """
    if cell is None:
        return []

    cell = str(cell).strip()

    if not cell:
        return []

    return [
        value.strip()
        for value in cell.split(separator)
        if value.strip()
    ]


def join_cell_values(values, separator):
    """
    Join entity values while removing duplicates and preserving order.
    """
    unique_values = []

    seen = set()

    for value in values:

        comparison_key = value.casefold()

        if comparison_key not in seen:
            seen.add(comparison_key)
            unique_values.append(value)

    return f" {separator} ".join(unique_values)


# ============================================================
# LOOKUP TABLE CONSTRUCTION
# ============================================================

def build_reference_lookups(
    reference_sections,
    ignore_case,
    ignore_accents,
    strip_whitespace,
):
    """
    Build normalized lookups for:
    - entity category
    - preferred TXT spelling
    - modifications

    Modification behavior:
    The left-hand value is converted to the right-hand value before
    entity classification.

    For example:

        Méjico -> México

    A TSV value of "Méjico" becomes "México", and "México" is then
    classified according to the approved People, Organizations, or
    Places list.
    """

    category_lookup = {}
    preferred_spelling_lookup = {}

    for category in [
        "people",
        "organizations",
        "places",
    ]:

        for value in reference_sections[category]:

            normalized = normalize_value(
                value,
                ignore_case=ignore_case,
                ignore_accents=ignore_accents,
                strip_whitespace=strip_whitespace,
            )

            category_lookup[normalized] = category
            preferred_spelling_lookup[normalized] = value

    modification_lookup = {}

    for old_value, new_value in reference_sections["modifications"]:

        normalized_old = normalize_value(
            old_value,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=strip_whitespace,
        )

        modification_lookup[normalized_old] = new_value

    return (
        category_lookup,
        preferred_spelling_lookup,
        modification_lookup,
    )


# ============================================================
# MAIN CLEANING LOGIC
# ============================================================

def clean_and_reorganize_dataframe(
    dataframe,
    category_columns,
    reference_sections,
    separator,
    ignore_case,
    ignore_accents,
    strip_whitespace,
):
    """
    Clean the three mapped TSV entity columns row by row.

    Processing order for each individual TSV value:

    1. Apply a TXT modification if one exists.
    2. Determine whether the resulting value belongs to People,
       Organizations, or Places.
    3. Remove it if it does not occur in any approved TXT entity list.
    4. Keep it in place if it is already in the correct TSV column.
    5. Move it to the correct TSV column if it appears in the wrong one.

    This preserves entity associations within the same TSV row.
    """

    cleaned_df = dataframe.copy()

    (
        category_lookup,
        preferred_spelling_lookup,
        modification_lookup,
    ) = build_reference_lookups(
        reference_sections=reference_sections,
        ignore_case=ignore_case,
        ignore_accents=ignore_accents,
        strip_whitespace=strip_whitespace,
    )

    stats = {
        "checked": 0,
        "kept": 0,
        "removed": 0,
        "moved": 0,
        "modified": 0,
    }

    removed_records = []
    moved_records = []
    modified_records = []

    entity_categories = [
        "people",
        "organizations",
        "places",
    ]

    # --------------------------------------------------------
    # Process one row at a time
    # --------------------------------------------------------

    for row_index in cleaned_df.index:

        # New entity values that will replace the original three cells.
        row_output = {
            "people": [],
            "organizations": [],
            "places": [],
        }

        for source_category in entity_categories:

            source_column = category_columns[source_category]

            original_cell = cleaned_df.at[
                row_index,
                source_column,
            ]

            values = split_cell_values(
                original_cell,
                separator,
            )

            for original_value in values:

                stats["checked"] += 1

                working_value = original_value

                # --------------------------------------------
                # STEP 1: Apply modification rule
                # --------------------------------------------

                normalized_original = normalize_value(
                    working_value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                if normalized_original in modification_lookup:

                    modified_value = modification_lookup[
                        normalized_original
                    ]

                    if modified_value != working_value:

                        stats["modified"] += 1

                        modified_records.append(
                            {
                                "row": row_index + 1,
                                "original_value": working_value,
                                "new_value": modified_value,
                            }
                        )

                    working_value = modified_value

                # --------------------------------------------
                # STEP 2: Identify approved entity category
                # --------------------------------------------

                normalized_working = normalize_value(
                    working_value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                destination_category = category_lookup.get(
                    normalized_working
                )

                # --------------------------------------------
                # STEP 3: Remove unapproved values
                # --------------------------------------------

                if destination_category is None:

                    stats["removed"] += 1

                    removed_records.append(
                        {
                            "row": row_index + 1,
                            "source_column": source_column,
                            "value": working_value,
                        }
                    )

                    continue

                # Use the preferred spelling from the TXT list.
                final_value = preferred_spelling_lookup.get(
                    normalized_working,
                    working_value,
                )

                # --------------------------------------------
                # STEP 4/5: Keep or move
                # --------------------------------------------

                row_output[
                    destination_category
                ].append(final_value)

                if destination_category == source_category:

                    stats["kept"] += 1

                else:

                    stats["moved"] += 1

                    moved_records.append(
                        {
                            "row": row_index + 1,
                            "value": final_value,
                            "source_column": source_column,
                            "destination_column": category_columns[
                                destination_category
                            ],
                        }
                    )

        # ----------------------------------------------------
        # Replace all three entity cells for this row
        # ----------------------------------------------------

        for category in entity_categories:

            column_name = category_columns[category]

            cleaned_df.at[
                row_index,
                column_name,
            ] = join_cell_values(
                row_output[category],
                separator,
            )

    return (
        cleaned_df,
        stats,
        removed_records,
        moved_records,
        modified_records,
    )


# ============================================================
# DOWNLOAD
# ============================================================

def make_tsv_download(dataframe):
    """
    Convert the DataFrame to UTF-8 TSV bytes.
    """
    return dataframe.to_csv(
        sep="\t",
        index=False,
        lineterminator="\n",
    ).encode("utf-8-sig")


# ============================================================
# LANGUAGE SELECTOR
# ============================================================

language = st.selectbox(
    "Language / Idioma",
    options=[
        "English",
        "Español",
        "Português",
    ],
)

t = TRANSLATIONS[language]


# ============================================================
# MAIN INTERFACE
# ============================================================

st.title(f"🧹 {t['app_title']}")

st.write(t["app_description"])

st.divider()


# ============================================================
# FILE UPLOADS
# ============================================================

upload_col1, upload_col2 = st.columns(2)

with upload_col1:

    tsv_file = st.file_uploader(
        t["upload_tsv"],
        type=["tsv"],
        help=t["tsv_help"],
    )

with upload_col2:

    txt_file = st.file_uploader(
        t["upload_txt"],
        type=["txt"],
        help=t["txt_help"],
    )


# ============================================================
# TXT FORMAT EXAMPLE
# ============================================================

with st.expander(t["txt_format"]):

    st.code(
        t["txt_format_example"],
        language="text",
    )


# ============================================================
# PROCESS FILES
# ============================================================

if tsv_file is not None and txt_file is not None:

    # --------------------------------------------------------
    # Read TSV
    # --------------------------------------------------------

    try:

        df = read_tsv(tsv_file)

    except Exception as error:

        st.error(
            f"{t['tsv_error']} {error}"
        )

        st.stop()

    # --------------------------------------------------------
    # Read TXT
    # --------------------------------------------------------

    try:

        txt_content = decode_uploaded_file(
            txt_file
        )

        (
            reference_sections,
            unrecognized_content,
        ) = parse_reference_txt(
            txt_content
        )

    except Exception as error:

        st.error(
            f"{t['txt_error']} {error}"
        )

        st.stop()


    # ========================================================
    # ORIGINAL TSV PREVIEW
    # ========================================================

    st.subheader(
        t["preview_original"]
    )

    st.dataframe(
        df.head(100),
        use_container_width=True,
    )


    # ========================================================
    # TXT REFERENCE SUMMARY
    # ========================================================

    st.subheader(
        t["reference_summary"]
    )

    summary_col1, summary_col2, summary_col3, summary_col4 = (
        st.columns(4)
    )

    summary_col1.metric(
        t["people"],
        len(reference_sections["people"]),
    )

    summary_col2.metric(
        t["organizations"],
        len(reference_sections["organizations"]),
    )

    summary_col3.metric(
        t["places"],
        len(reference_sections["places"]),
    )

    summary_col4.metric(
        t["modifications"],
        len(reference_sections["modifications"]),
    )


    # ========================================================
    # COLUMN MAPPING
    # ========================================================

    st.divider()

    st.subheader(
        t["mapping"]
    )

    st.caption(
        t["mapping_help"]
    )

    column_names = list(df.columns)

    map_col1, map_col2, map_col3 = st.columns(3)

    with map_col1:

        people_column = st.selectbox(
            t["people_column"],
            options=column_names,
            index=0,
        )

    with map_col2:

        default_org_index = (
            1
            if len(column_names) > 1
            else 0
        )

        organizations_column = st.selectbox(
            t["organizations_column"],
            options=column_names,
            index=default_org_index,
        )

    with map_col3:

        default_place_index = (
            2
            if len(column_names) > 2
            else 0
        )

        places_column = st.selectbox(
            t["places_column"],
            options=column_names,
            index=default_place_index,
        )


    # ========================================================
    # SETTINGS
    # ========================================================

    st.subheader(
        t["comparison_settings"]
    )

    settings_col1, settings_col2 = st.columns(2)

    with settings_col1:

        separator_options = {
            "Pipe |": "|",
            "Semicolon ;": ";",
            "Comma ,": ",",
        }

        selected_separator_label = st.selectbox(
            t["separator"],
            options=list(
                separator_options.keys()
            ),
            index=0,
        )

        separator = separator_options[
            selected_separator_label
        ]

    with settings_col2:

        ignore_case = st.checkbox(
            t["case_insensitive"],
            value=True,
        )

        ignore_accents = st.checkbox(
            t["accent_insensitive"],
            value=False,
        )

        strip_whitespace = st.checkbox(
            t["strip_whitespace"],
            value=True,
        )


    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    if st.button(
        t["process"],
        type="primary",
        use_container_width=True,
    ):

        selected_entity_columns = [
            people_column,
            organizations_column,
            places_column,
        ]

        if len(
            set(selected_entity_columns)
        ) != 3:

            st.error(
                t["same_columns_error"]
            )

            st.stop()

        category_columns = {
            "people": people_column,
            "organizations": organizations_column,
            "places": places_column,
        }

        (
            cleaned_df,
            stats,
            removed_records,
            moved_records,
            modified_records,
        ) = clean_and_reorganize_dataframe(
            dataframe=df,
            category_columns=category_columns,
            reference_sections=reference_sections,
            separator=separator,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=strip_whitespace,
        )

        st.success(
            t["success"]
        )


        # ====================================================
        # RESULTS
        # ====================================================

        st.subheader(
            t["results"]
        )

        result_col1, result_col2, result_col3 = (
            st.columns(3)
        )

        result_col1.metric(
            t["rows"],
            f"{len(cleaned_df):,}",
        )

        result_col2.metric(
            t["values_checked"],
            f"{stats['checked']:,}",
        )

        result_col3.metric(
            t["values_kept"],
            f"{stats['kept']:,}",
        )

        result_col4, result_col5, result_col6 = (
            st.columns(3)
        )

        result_col4.metric(
            t["values_removed"],
            f"{stats['removed']:,}",
        )

        result_col5.metric(
            t["values_moved"],
            f"{stats['moved']:,}",
        )

        result_col6.metric(
            t["values_modified"],
            f"{stats['modified']:,}",
        )


        # ====================================================
        # CLEANED TSV PREVIEW
        # ====================================================

        st.subheader(
            t["preview_cleaned"]
        )

        st.dataframe(
            cleaned_df.head(100),
            use_container_width=True,
        )


        # ====================================================
        # MOVED VALUES REPORT
        # ====================================================

        with st.expander(
            f"{t['moved_values']} ({stats['moved']:,})"
        ):

            if moved_records:

                moved_df = pd.DataFrame(
                    moved_records
                )

                moved_summary = (
                    moved_df
                    .groupby(
                        [
                            "value",
                            "source_column",
                            "destination_column",
                        ],
                        dropna=False,
                    )
                    .size()
                    .reset_index(
                        name="count"
                    )
                    .rename(
                        columns={
                            "value": t["value"],
                            "source_column": t["source_column"],
                            "destination_column": t["destination_column"],
                            "count": t["count"],
                        }
                    )
                )

                st.dataframe(
                    moved_summary,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    t["no_moved"]
                )


        # ====================================================
        # MODIFIED VALUES REPORT
        # ====================================================

        with st.expander(
            f"{t['modified_values']} ({stats['modified']:,})"
        ):

            if modified_records:

                modification_counter = Counter(
                    (
                        record["original_value"],
                        record["new_value"],
                    )
                    for record in modified_records
                )

                modification_summary = pd.DataFrame(
                    [
                        {
                            t["original_value"]: old_value,
                            t["new_value"]: new_value,
                            t["count"]: count,
                        }
                        for (
                            old_value,
                            new_value,
                        ), count in modification_counter.items()
                    ]
                )

                st.dataframe(
                    modification_summary,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    t["no_modified"]
                )


        # ====================================================
        # REMOVED VALUES REPORT
        # ====================================================

        with st.expander(
            f"{t['removed_values']} ({stats['removed']:,})"
        ):

            if removed_records:

                removed_df = pd.DataFrame(
                    removed_records
                )

                removed_summary = (
                    removed_df
                    .groupby(
                        [
                            "source_column",
                            "value",
                        ],
                        dropna=False,
                    )
                    .size()
                    .reset_index(
                        name="count"
                    )
                    .rename(
                        columns={
                            "source_column": t["source_column"],
                            "value": t["value"],
                            "count": t["count"],
                        }
                    )
                )

                st.dataframe(
                    removed_summary,
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    t["no_removed"]
                )


        # ====================================================
        # DOWNLOAD
        # ====================================================

        cleaned_tsv_bytes = make_tsv_download(
            cleaned_df
        )

        st.download_button(
            label=t["download"],
            data=cleaned_tsv_bytes,
            file_name=t["download_name"],
            mime="text/tab-separated-values",
            type="primary",
            use_container_width=True,
        )

else:

    st.info(
        t["missing_files"]
    )
