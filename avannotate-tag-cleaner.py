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
            "columns, together with a TXT reference file containing People, "
            "Organizations, Places, and Modifications lists. The app first "
            "reorganizes TSV values according to the TXT categories, then removes "
            "values that do not appear in the TXT category lists, applies the "
            "requested modifications, and adds a combined Tags column."
        ),
        "upload_tsv": "Upload TSV file",
        "upload_txt": "Upload TXT reference list",
        "tsv_help": "Upload a tab-separated values (.tsv) file.",
        "txt_help": (
            "Upload a TXT file with sections for People, Organizations, "
            "Places, and Modifications."
        ),
        "mapping": "TSV column mapping",
        "mapping_help": (
            "Select the TSV column corresponding to each TXT entity category."
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
        "updated_txt_preview": "Updated TXT entity list preview",
        "people": "People",
        "organizations": "Organizations",
        "places": "Places",
        "modifications": "Modifications",
        "results": "Processing results",
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
        "download_tsv": "Download cleaned TSV",
        "download_txt": "Download updated TXT entity list",
        "download_tsv_name": "cleaned.tsv",
        "download_txt_name": "updated_entities.txt",
        "missing_files": "Upload both a TSV file and a TXT file to continue.",
        "same_columns_error": (
            "The People, Organizations, and Places mappings must use "
            "three different TSV columns."
        ),
        "tsv_error": "The TSV file could not be read.",
        "txt_error": "The TXT file could not be read.",
        "success": "The TSV file and updated TXT entity list were generated successfully.",
        "txt_format": "Expected TXT format",
        "unrecognized_content": "Content found before a recognized TXT heading",
        "unrecognized_help": (
            "These lines were not processed because they appeared before a "
            "recognized People, Organizations, Places, or Modifications heading."
        ),
        "txt_format_example": """People
Villa, Francisco
Madero, Francisco I.

Organizations
University of Texas
UNESCO

Places
Mexico
Chihuahua
Austin

Modifications
Mexico -> México
University of Texas -> The University of Texas at Austin
""",
    },

    "Español": {
        "app_title": "Depurador de entidades en TSV",
        "app_description": (
            "Suba un archivo TSV con columnas de nombres de personas, organizaciones "
            "y lugares, junto con un archivo TXT de referencia que contenga listas de "
            "Personas, Organizaciones, Lugares y Modificaciones. La aplicación primero "
            "reorganiza los valores del TSV según las categorías del TXT, después "
            "elimina los valores que no aparecen en las listas del TXT, aplica las "
            "modificaciones solicitadas y añade una columna combinada llamada Tags."
        ),
        "upload_tsv": "Subir archivo TSV",
        "upload_txt": "Subir lista de referencia TXT",
        "tsv_help": "Suba un archivo de valores separados por tabulaciones (.tsv).",
        "txt_help": (
            "Suba un archivo TXT con secciones para Personas, Organizaciones, "
            "Lugares y Modificaciones."
        ),
        "mapping": "Correspondencia de columnas TSV",
        "mapping_help": (
            "Seleccione la columna TSV correspondiente a cada categoría de entidades del TXT."
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
        "updated_txt_preview": "Vista previa de la lista TXT actualizada",
        "people": "Personas",
        "organizations": "Organizaciones",
        "places": "Lugares",
        "modifications": "Modificaciones",
        "results": "Resultados del procesamiento",
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
        "download_tsv": "Descargar TSV depurado",
        "download_txt": "Descargar lista TXT de entidades actualizada",
        "download_tsv_name": "tsv_depurado.tsv",
        "download_txt_name": "entidades_actualizadas.txt",
        "missing_files": "Suba un archivo TSV y un archivo TXT para continuar.",
        "same_columns_error": (
            "Las correspondencias de Personas, Organizaciones y Lugares deben "
            "utilizar tres columnas TSV diferentes."
        ),
        "tsv_error": "No se pudo leer el archivo TSV.",
        "txt_error": "No se pudo leer el archivo TXT.",
        "success": "El TSV y la lista TXT de entidades actualizada se generaron correctamente.",
        "txt_format": "Formato TXT esperado",
        "unrecognized_content": "Contenido encontrado antes de un encabezado TXT reconocido",
        "unrecognized_help": (
            "Estas líneas no se procesaron porque aparecieron antes de un encabezado "
            "reconocido de Personas, Organizaciones, Lugares o Modificaciones."
        ),
        "txt_format_example": """Personas
Villa, Francisco
Madero, Francisco I.

Organizaciones
University of Texas
UNESCO

Lugares
México
Chihuahua
Austin

Modificaciones
Mexico -> México
University of Texas -> The University of Texas at Austin
""",
    },

    "Português": {
        "app_title": "Limpador de entidades em TSV",
        "app_description": (
            "Envie um arquivo TSV com colunas de nomes de pessoas, organizações "
            "e lugares, juntamente com um arquivo TXT de referência contendo listas "
            "de Pessoas, Organizações, Lugares e Modificações. O aplicativo primeiro "
            "reorganiza os valores do TSV de acordo com as categorias do TXT, depois "
            "remove os valores ausentes das listas do TXT, aplica as modificações "
            "solicitadas e adiciona uma coluna combinada chamada Tags."
        ),
        "upload_tsv": "Enviar arquivo TSV",
        "upload_txt": "Enviar lista de referência TXT",
        "tsv_help": "Envie um arquivo de valores separados por tabulação (.tsv).",
        "txt_help": (
            "Envie um arquivo TXT com seções para Pessoas, Organizações, "
            "Lugares e Modificações."
        ),
        "mapping": "Mapeamento das colunas TSV",
        "mapping_help": (
            "Selecione a coluna TSV correspondente a cada categoria de entidade do TXT."
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
        "updated_txt_preview": "Visualização da lista TXT atualizada",
        "people": "Pessoas",
        "organizations": "Organizações",
        "places": "Lugares",
        "modifications": "Modificações",
        "results": "Resultados do processamento",
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
        "download_tsv": "Baixar TSV limpo",
        "download_txt": "Baixar lista TXT de entidades atualizada",
        "download_tsv_name": "tsv_limpo.tsv",
        "download_txt_name": "entidades_atualizadas.txt",
        "missing_files": "Envie um arquivo TSV e um arquivo TXT para continuar.",
        "same_columns_error": (
            "Os mapeamentos de Pessoas, Organizações e Lugares devem usar "
            "três colunas TSV diferentes."
        ),
        "tsv_error": "Não foi possível ler o arquivo TSV.",
        "txt_error": "Não foi possível ler o arquivo TXT.",
        "success": "O TSV e a lista TXT de entidades atualizada foram gerados com sucesso.",
        "txt_format": "Formato TXT esperado",
        "unrecognized_content": "Conteúdo encontrado antes de um cabeçalho TXT reconhecido",
        "unrecognized_help": (
            "Estas linhas não foram processadas porque apareceram antes de um "
            "cabeçalho reconhecido de Pessoas, Organizações, Lugares ou Modificações."
        ),
        "txt_format_example": """Pessoas
Villa, Francisco
Madero, Francisco I.

Organizações
University of Texas
UNESCO

Lugares
México
Chihuahua
Austin

Modificações
Mexico -> México
University of Texas -> The University of Texas at Austin
""",
    },
}


# ============================================================
# TXT SECTION HEADING ALIASES
# ============================================================

SECTION_ALIASES = {
    "people": {
        "people",
        "person",
        "persons",
        "people names",
        "person names",
        "personas",
        "persona",
        "nombres de personas",
        "pessoas",
        "pessoa",
        "nomes de pessoas",
    },

    "organizations": {
        "organizations",
        "organization",
        "organisations",
        "organisation",
        "organization names",
        "organisation names",
        "organizaciones",
        "organización",
        "nombres de organizaciones",
        "organizacoes",
        "organizações",
        "organização",
        "nomes de organizações",
    },

    "places": {
        "places",
        "place",
        "locations",
        "location",
        "place names",
        "location names",
        "lugares",
        "lugar",
        "nombres de lugares",
        "locais",
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
    Read the TSV entirely as strings so textual content,
    identifiers, and empty cells are preserved.
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
    Normalize TXT section headings for recognition across
    English, Spanish, and Portuguese.
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
    Parse the TXT reference file.

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
        Mexico -> México
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

        if section_heading is not None:
            current_section = section_heading
            continue

        if current_section is None:
            unrecognized_content.append(line)
            continue

        if current_section == "modifications":

            if "->" not in line:
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
            dict.fromkeys(
                sections[section_name]
            )
        )

    sections["modifications"] = list(
        dict.fromkeys(
            sections["modifications"]
        )
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


def deduplicate_values(
    values,
    ignore_case=True,
    ignore_accents=False,
):
    """
    Remove duplicate values while preserving original order.
    """
    unique_values = []
    seen = set()

    for value in values:

        comparison_key = normalize_value(
            value=value,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=True,
        )

        if comparison_key not in seen:
            seen.add(comparison_key)
            unique_values.append(value)

    return unique_values


def join_cell_values(
    values,
    separator,
    ignore_case=True,
    ignore_accents=False,
):
    """
    Join multiple entity values using the selected cell separator.
    """
    unique_values = deduplicate_values(
        values=values,
        ignore_case=ignore_case,
        ignore_accents=ignore_accents,
    )

    return f" {separator} ".join(unique_values)


# ============================================================
# REFERENCE LOOKUP CONSTRUCTION
# ============================================================

def build_reference_lookups(
    reference_sections,
    ignore_case,
    ignore_accents,
    strip_whitespace,
):
    """
    Build separate lookups for:

    1. Entity category.
    2. Preferred TXT spelling.
    3. Modifications.

    Processing order:

        Original TSV value
            ↓
        Determine TXT category
            ↓
        Move to correct TSV column
            ↓
        Delete if absent from all category lists
            ↓
        Apply modification
    """

    category_lookup = {}
    preferred_spelling_lookup = {}
    modification_lookup = {}

    for category in [
        "people",
        "organizations",
        "places",
    ]:

        for value in reference_sections[category]:

            normalized = normalize_value(
                value=value,
                ignore_case=ignore_case,
                ignore_accents=ignore_accents,
                strip_whitespace=strip_whitespace,
            )

            category_lookup[normalized] = category
            preferred_spelling_lookup[normalized] = value

    for old_value, new_value in reference_sections["modifications"]:

        normalized_old = normalize_value(
            value=old_value,
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
# MAIN TSV PROCESSING
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
    Process the TSV in this exact order:

    STEP 1 — REORGANIZE
        Determine the category of each original TSV value using
        the TXT People, Organizations, and Places lists.

    STEP 2 — DELETE
        Remove values absent from all three TXT category lists.

    STEP 3 — MODIFY
        Apply matching old value -> new value rules only after
        category validation and reorganization.

    STEP 4 — TAGS
        Create a final Tags column combining all resulting values
        from the People, Organizations, and Places columns.

        Tags are separated by exactly:

            " | "
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

    # ========================================================
    # PROCESS ONE TSV ROW AT A TIME
    # ========================================================

    for row_index in cleaned_df.index:

        row_output = {
            "people": [],
            "organizations": [],
            "places": [],
        }

        for source_category in entity_categories:

            source_column = category_columns[
                source_category
            ]

            original_cell = cleaned_df.at[
                row_index,
                source_column,
            ]

            values = split_cell_values(
                cell=original_cell,
                separator=separator,
            )

            for original_value in values:

                stats["checked"] += 1

                # ==================================================
                # STEP 1:
                # DETERMINE CATEGORY FROM ORIGINAL TSV VALUE
                # ==================================================

                normalized_original = normalize_value(
                    value=original_value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                destination_category = category_lookup.get(
                    normalized_original
                )

                # ==================================================
                # STEP 2:
                # DELETE IF ABSENT FROM ALL TXT CATEGORY LISTS
                # ==================================================

                if destination_category is None:

                    stats["removed"] += 1

                    removed_records.append(
                        {
                            "row": row_index + 1,
                            "source_column": source_column,
                            "value": original_value,
                        }
                    )

                    continue

                # Use spelling from TXT category list.
                categorized_value = preferred_spelling_lookup.get(
                    normalized_original,
                    original_value,
                )

                # Record whether the value stayed or moved.
                if destination_category == source_category:

                    stats["kept"] += 1

                else:

                    stats["moved"] += 1

                    moved_records.append(
                        {
                            "row": row_index + 1,
                            "value": categorized_value,
                            "source_column": source_column,
                            "destination_column": category_columns[
                                destination_category
                            ],
                        }
                    )

                # ==================================================
                # STEP 3:
                # APPLY MODIFICATION
                # ==================================================

                normalized_categorized_value = normalize_value(
                    value=categorized_value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                if normalized_categorized_value in modification_lookup:

                    final_value = modification_lookup[
                        normalized_categorized_value
                    ]

                    if final_value != categorized_value:

                        stats["modified"] += 1

                        modified_records.append(
                            {
                                "row": row_index + 1,
                                "original_value": categorized_value,
                                "new_value": final_value,
                            }
                        )

                else:

                    final_value = categorized_value

                # A modification changes the displayed value,
                # but does not change the category determined earlier.
                row_output[
                    destination_category
                ].append(
                    final_value
                )

        # ====================================================
        # WRITE REORGANIZED ENTITY COLUMNS BACK TO TSV
        # ====================================================

        for category in entity_categories:

            column_name = category_columns[
                category
            ]

            cleaned_df.at[
                row_index,
                column_name,
            ] = join_cell_values(
                values=row_output[category],
                separator=separator,
                ignore_case=ignore_case,
                ignore_accents=ignore_accents,
            )

    # ========================================================
    # STEP 4:
    # CREATE FINAL TAGS COLUMN
    # ========================================================

    tags_values = []

    for row_index in cleaned_df.index:

        combined_values = []

        # Keep this order:
        # People → Organizations → Places
        for category in [
            "people",
            "organizations",
            "places",
        ]:

            column_name = category_columns[
                category
            ]

            cell_values = split_cell_values(
                cell=cleaned_df.at[
                    row_index,
                    column_name,
                ],
                separator=separator,
            )

            combined_values.extend(
                cell_values
            )

        combined_values = deduplicate_values(
            values=combined_values,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
        )

        tags_values.append(
            " | ".join(
                combined_values
            )
        )

    # If the original TSV already contains a Tags column,
    # this replaces it with the newly generated final Tags column.
    cleaned_df["Tags"] = tags_values

    # Ensure Tags appears at the very end of the TSV.
    columns_without_tags = [
        column
        for column in cleaned_df.columns
        if column != "Tags"
    ]

    cleaned_df = cleaned_df[
        columns_without_tags
        + ["Tags"]
    ]

    return (
        cleaned_df,
        stats,
        removed_records,
        moved_records,
        modified_records,
    )


# ============================================================
# UPDATED TXT REFERENCE LIST
# ============================================================

def apply_modifications_to_reference_sections(
    reference_sections,
    ignore_case,
    ignore_accents,
    strip_whitespace,
):
    """
    Create a new entity reference list with all requested
    modifications already reflected.

    Example input:

        Places
        Mexico

        Modifications
        Mexico -> México

    Updated TXT output:

        Places
        México

    The updated TXT contains only:
        People
        Organizations
        Places

    The Modifications section is omitted because its changes
    have already been incorporated into the entity lists.
    """

    modification_lookup = {}

    for old_value, new_value in reference_sections["modifications"]:

        normalized_old = normalize_value(
            value=old_value,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=strip_whitespace,
        )

        modification_lookup[
            normalized_old
        ] = new_value

    updated_sections = {
        "people": [],
        "organizations": [],
        "places": [],
    }

    for category in [
        "people",
        "organizations",
        "places",
    ]:

        updated_values = []

        for value in reference_sections[
            category
        ]:

            normalized_value = normalize_value(
                value=value,
                ignore_case=ignore_case,
                ignore_accents=ignore_accents,
                strip_whitespace=strip_whitespace,
            )

            updated_value = modification_lookup.get(
                normalized_value,
                value,
            )

            updated_values.append(
                updated_value
            )

        # Remove duplicates created by modifications.
        updated_sections[
            category
        ] = deduplicate_values(
            values=updated_values,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
        )

    return updated_sections


def make_updated_txt(
    updated_sections,
):
    """
    Generate a clean TXT reference list with modifications
    already incorporated.

    Output headings remain in English so that the generated file
    can be uploaded directly back into this app regardless of the
    selected interface language.
    """

    lines = []

    lines.append(
        "People"
    )

    lines.extend(
        updated_sections[
            "people"
        ]
    )

    lines.append("")
    lines.append(
        "Organizations"
    )

    lines.extend(
        updated_sections[
            "organizations"
        ]
    )

    lines.append("")
    lines.append(
        "Places"
    )

    lines.extend(
        updated_sections[
            "places"
        ]
    )

    return "\n".join(
        lines
    ).strip() + "\n"


# ============================================================
# DOWNLOAD HELPERS
# ============================================================

def make_tsv_download(dataframe):
    """
    Convert the DataFrame to UTF-8 TSV bytes.
    """
    return dataframe.to_csv(
        sep="\t",
        index=False,
        lineterminator="\n",
    ).encode(
        "utf-8-sig"
    )


def make_txt_download(text):
    """
    Convert TXT content to UTF-8 bytes.
    """
    return text.encode(
        "utf-8-sig"
    )


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

t = TRANSLATIONS[
    language
]


# ============================================================
# MAIN INTERFACE
# ============================================================

st.title(
    f"🧹 {t['app_title']}"
)

st.write(
    t["app_description"]
)

st.divider()


# ============================================================
# FILE UPLOADS
# ============================================================

upload_col1, upload_col2 = st.columns(2)


with upload_col1:

    tsv_file = st.file_uploader(
        t["upload_tsv"],
        type=[
            "tsv",
        ],
        help=t["tsv_help"],
    )


with upload_col2:

    txt_file = st.file_uploader(
        t["upload_txt"],
        type=[
            "txt",
        ],
        help=t["txt_help"],
    )


# ============================================================
# TXT FORMAT EXAMPLE
# ============================================================

with st.expander(
    t["txt_format"]
):

    st.code(
        t["txt_format_example"],
        language="text",
    )


# ============================================================
# PROCESS UPLOADED FILES
# ============================================================

if (
    tsv_file is not None
    and txt_file is not None
):

    # ========================================================
    # READ TSV
    # ========================================================

    try:

        df = read_tsv(
            tsv_file
        )

    except Exception as error:

        st.error(
            f"{t['tsv_error']} {error}"
        )

        st.stop()


    # ========================================================
    # READ AND PARSE TXT
    # ========================================================

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
        len(
            reference_sections[
                "people"
            ]
        ),
    )

    summary_col2.metric(
        t["organizations"],
        len(
            reference_sections[
                "organizations"
            ]
        ),
    )

    summary_col3.metric(
        t["places"],
        len(
            reference_sections[
                "places"
            ]
        ),
    )

    summary_col4.metric(
        t["modifications"],
        len(
            reference_sections[
                "modifications"
            ]
        ),
    )


    # ========================================================
    # SHOW UNRECOGNIZED TXT CONTENT
    # ========================================================

    if unrecognized_content:

        with st.expander(
            t["unrecognized_content"]
        ):

            st.caption(
                t["unrecognized_help"]
            )

            st.code(
                "\n".join(
                    unrecognized_content
                ),
                language="text",
            )


    # ========================================================
    # TSV COLUMN MAPPING
    # ========================================================

    st.divider()

    st.subheader(
        t["mapping"]
    )

    st.caption(
        t["mapping_help"]
    )

    column_names = list(
        df.columns
    )


    def find_default_column_index(
        columns,
        keywords,
        fallback_index,
    ):
        """
        Find the first TSV column containing one of the supplied
        keywords. Otherwise use the fallback index.
        """

        for index, column in enumerate(
            columns
        ):

            normalized_column = normalize_heading(
                column
            )

            for keyword in keywords:

                if keyword in normalized_column:
                    return index

        if len(columns) == 0:
            return 0

        return min(
            fallback_index,
            len(columns) - 1,
        )


    people_default_index = find_default_column_index(
        columns=column_names,
        keywords=[
            "people",
            "person",
            "persona",
            "pessoa",
        ],
        fallback_index=0,
    )


    organizations_default_index = find_default_column_index(
        columns=column_names,
        keywords=[
            "organization",
            "organisation",
            "organizacion",
            "organizacao",
        ],
        fallback_index=1,
    )


    places_default_index = find_default_column_index(
        columns=column_names,
        keywords=[
            "place",
            "location",
            "lugar",
            "local",
        ],
        fallback_index=2,
    )


    map_col1, map_col2, map_col3 = st.columns(3)


    with map_col1:

        people_column = st.selectbox(
            t["people_column"],
            options=column_names,
            index=people_default_index,
        )


    with map_col2:

        organizations_column = st.selectbox(
            t["organizations_column"],
            options=column_names,
            index=organizations_default_index,
        )


    with map_col3:

        places_column = st.selectbox(
            t["places_column"],
            options=column_names,
            index=places_default_index,
        )


    # ========================================================
    # COMPARISON SETTINGS
    # ========================================================

    st.subheader(
        t["comparison_settings"]
    )

    settings_col1, settings_col2 = (
        st.columns(2)
    )


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
            set(
                selected_entity_columns
            )
        ) != 3:

            st.error(
                t[
                    "same_columns_error"
                ]
            )

            st.stop()


        category_columns = {
            "people": people_column,
            "organizations": organizations_column,
            "places": places_column,
        }


        # ====================================================
        # RUN TSV PROCESSING
        # ====================================================

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


        # ====================================================
        # GENERATE UPDATED TXT REFERENCE LIST
        # ====================================================

        updated_reference_sections = (
            apply_modifications_to_reference_sections(
                reference_sections=reference_sections,
                ignore_case=ignore_case,
                ignore_accents=ignore_accents,
                strip_whitespace=strip_whitespace,
            )
        )

        updated_txt_content = make_updated_txt(
            updated_reference_sections
        )


        st.success(
            t["success"]
        )


        # ====================================================
        # RESULTS METRICS
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
            f"{t['moved_values']} "
            f"({stats['moved']:,})"
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
                    .sort_values(
                        [
                            "destination_column",
                            "value",
                        ]
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
        # REMOVED VALUES REPORT
        # ====================================================

        with st.expander(
            f"{t['removed_values']} "
            f"({stats['removed']:,})"
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
                    .sort_values(
                        [
                            "source_column",
                            "value",
                        ]
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
        # MODIFIED VALUES REPORT
        # ====================================================

        with st.expander(
            f"{t['modified_values']} "
            f"({stats['modified']:,})"
        ):

            if modified_records:

                modification_counter = Counter(
                    (
                        record[
                            "original_value"
                        ],
                        record[
                            "new_value"
                        ],
                    )
                    for record
                    in modified_records
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
                        ), count
                        in modification_counter.items()
                    ]
                )

                modification_summary = (
                    modification_summary
                    .sort_values(
                        [
                            t["original_value"],
                            t["new_value"],
                        ]
                    )
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
        # UPDATED TXT PREVIEW
        # ====================================================

        with st.expander(
            t["updated_txt_preview"]
        ):

            st.code(
                updated_txt_content,
                language="text",
            )


        # ====================================================
        # DOWNLOADS
        # ====================================================

        cleaned_tsv_bytes = make_tsv_download(
            cleaned_df
        )

        updated_txt_bytes = make_txt_download(
            updated_txt_content
        )


        download_col1, download_col2 = st.columns(2)


        with download_col1:

            st.download_button(
                label=t["download_tsv"],
                data=cleaned_tsv_bytes,
                file_name=t["download_tsv_name"],
                mime="text/tab-separated-values",
                type="primary",
                use_container_width=True,
            )


        with download_col2:

            st.download_button(
                label=t["download_txt"],
                data=updated_txt_bytes,
                file_name=t["download_txt_name"],
                mime="text/plain",
                type="primary",
                use_container_width=True,
            )


# ============================================================
# WAITING FOR FILES
# ============================================================

else:

    st.info(
        t["missing_files"]
    )
