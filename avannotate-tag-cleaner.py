import io
import re
import unicodedata

import pandas as pd
import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TSV Name List Cleaner",
    page_icon="🧹",
    layout="wide",
)


# ============================================================
# INTERFACE TRANSLATIONS
# ============================================================

TRANSLATIONS = {
    "English": {
        "app_title": "TSV Name List Cleaner",
        "app_description": (
            "Upload a TSV file containing columns with people, organization, "
            "and place names, along with a TXT file containing the approved "
            "values. The app will remove values from the selected TSV columns "
            "when they are not present in the TXT list."
        ),
        "language": "Interface language",
        "upload_tsv": "Upload TSV file",
        "upload_txt": "Upload TXT list",
        "tsv_help": "Upload a tab-separated values (.tsv) file.",
        "txt_help": (
            "Upload a plain-text (.txt) file containing the approved names or "
            "values, preferably one value per line."
        ),
        "settings": "Comparison settings",
        "select_columns": "Select columns to clean",
        "select_columns_help": (
            "Choose the columns containing people, organization, or place names. "
            "All other columns will remain unchanged."
        ),
        "separator": "Separator between multiple values in a TSV cell",
        "separator_help": (
            "For example, if a cell contains 'Mexico | Texas | Austin', "
            "select the pipe character (|)."
        ),
        "txt_format": "How are values separated in the TXT file?",
        "txt_lines": "One value per line",
        "txt_pipe": "Pipe character (|)",
        "txt_comma": "Comma",
        "txt_semicolon": "Semicolon",
        "case_insensitive": "Ignore capitalization",
        "accent_insensitive": "Ignore accents/diacritics",
        "strip_whitespace": "Ignore extra surrounding whitespace",
        "remove_empty": "Leave cleaned cells blank when no valid values remain",
        "preview_list": "Approved-value list preview",
        "approved_values": "approved values found",
        "process": "Clean TSV",
        "preview_original": "Original TSV preview",
        "preview_cleaned": "Cleaned TSV preview",
        "results": "Cleaning results",
        "rows": "Rows",
        "values_checked": "Values checked",
        "values_kept": "Values kept",
        "values_removed": "Values removed",
        "removed_values": "Removed values",
        "removed_value": "Removed value",
        "column": "Column",
        "count": "Count",
        "no_removed": "No values were removed.",
        "download": "Download cleaned TSV",
        "download_name": "cleaned.tsv",
        "missing_files": "Upload both a TSV file and a TXT file to continue.",
        "no_columns": "Select at least one TSV column to clean.",
        "empty_txt": "The TXT file does not contain any usable values.",
        "tsv_error": "The TSV file could not be read.",
        "txt_error": "The TXT file could not be read.",
        "success": "The TSV file was cleaned successfully.",
        "detected_columns": "TSV columns detected",
        "all_values": "All approved values",
    },
    "Español": {
        "app_title": "Depurador de nombres en TSV",
        "app_description": (
            "Suba un archivo TSV con columnas que contengan nombres de personas, "
            "organizaciones y lugares, junto con un archivo TXT que contenga los "
            "valores autorizados. La aplicación eliminará de las columnas "
            "seleccionadas los valores que no aparezcan en la lista TXT."
        ),
        "language": "Idioma de la interfaz",
        "upload_tsv": "Subir archivo TSV",
        "upload_txt": "Subir lista TXT",
        "tsv_help": "Suba un archivo de valores separados por tabulaciones (.tsv).",
        "txt_help": (
            "Suba un archivo de texto (.txt) con los nombres o valores "
            "autorizados, preferentemente un valor por línea."
        ),
        "settings": "Configuración de la comparación",
        "select_columns": "Seleccione las columnas que desea depurar",
        "select_columns_help": (
            "Seleccione las columnas que contienen nombres de personas, "
            "organizaciones o lugares. Las demás columnas no se modificarán."
        ),
        "separator": "Separador entre varios valores en una celda TSV",
        "separator_help": (
            "Por ejemplo, si una celda contiene 'México | Texas | Austin', "
            "seleccione el carácter de barra vertical (|)."
        ),
        "txt_format": "¿Cómo están separados los valores en el archivo TXT?",
        "txt_lines": "Un valor por línea",
        "txt_pipe": "Barra vertical (|)",
        "txt_comma": "Coma",
        "txt_semicolon": "Punto y coma",
        "case_insensitive": "Ignorar diferencias entre mayúsculas y minúsculas",
        "accent_insensitive": "Ignorar acentos y signos diacríticos",
        "strip_whitespace": "Ignorar espacios adicionales al principio y al final",
        "remove_empty": "Dejar la celda en blanco si no queda ningún valor válido",
        "preview_list": "Vista previa de la lista de valores autorizados",
        "approved_values": "valores autorizados encontrados",
        "process": "Depurar TSV",
        "preview_original": "Vista previa del TSV original",
        "preview_cleaned": "Vista previa del TSV depurado",
        "results": "Resultados de la depuración",
        "rows": "Filas",
        "values_checked": "Valores revisados",
        "values_kept": "Valores conservados",
        "values_removed": "Valores eliminados",
        "removed_values": "Valores eliminados",
        "removed_value": "Valor eliminado",
        "column": "Columna",
        "count": "Cantidad",
        "no_removed": "No se eliminó ningún valor.",
        "download": "Descargar TSV depurado",
        "download_name": "tsv_depurado.tsv",
        "missing_files": "Suba un archivo TSV y un archivo TXT para continuar.",
        "no_columns": "Seleccione al menos una columna del TSV para depurar.",
        "empty_txt": "El archivo TXT no contiene valores utilizables.",
        "tsv_error": "No se pudo leer el archivo TSV.",
        "txt_error": "No se pudo leer el archivo TXT.",
        "success": "El archivo TSV se depuró correctamente.",
        "detected_columns": "Columnas detectadas en el TSV",
        "all_values": "Todos los valores autorizados",
    },
    "Português": {
        "app_title": "Limpador de nomes em TSV",
        "app_description": (
            "Envie um arquivo TSV com colunas que contenham nomes de pessoas, "
            "organizações e lugares, juntamente com um arquivo TXT contendo os "
            "valores autorizados. O aplicativo removerá das colunas selecionadas "
            "os valores que não aparecem na lista TXT."
        ),
        "language": "Idioma da interface",
        "upload_tsv": "Enviar arquivo TSV",
        "upload_txt": "Enviar lista TXT",
        "tsv_help": "Envie um arquivo de valores separados por tabulação (.tsv).",
        "txt_help": (
            "Envie um arquivo de texto (.txt) com os nomes ou valores "
            "autorizados, preferencialmente um valor por linha."
        ),
        "settings": "Configurações de comparação",
        "select_columns": "Selecione as colunas para limpar",
        "select_columns_help": (
            "Escolha as colunas que contêm nomes de pessoas, organizações ou "
            "lugares. Todas as outras colunas permanecerão inalteradas."
        ),
        "separator": "Separador entre vários valores em uma célula TSV",
        "separator_help": (
            "Por exemplo, se uma célula contém 'México | Texas | Austin', "
            "selecione o caractere de barra vertical (|)."
        ),
        "txt_format": "Como os valores estão separados no arquivo TXT?",
        "txt_lines": "Um valor por linha",
        "txt_pipe": "Barra vertical (|)",
        "txt_comma": "Vírgula",
        "txt_semicolon": "Ponto e vírgula",
        "case_insensitive": "Ignorar diferenças entre maiúsculas e minúsculas",
        "accent_insensitive": "Ignorar acentos e sinais diacríticos",
        "strip_whitespace": "Ignorar espaços extras no início e no final",
        "remove_empty": "Deixar a célula vazia quando nenhum valor válido permanecer",
        "preview_list": "Visualização da lista de valores autorizados",
        "approved_values": "valores autorizados encontrados",
        "process": "Limpar TSV",
        "preview_original": "Visualização do TSV original",
        "preview_cleaned": "Visualização do TSV limpo",
        "results": "Resultados da limpeza",
        "rows": "Linhas",
        "values_checked": "Valores verificados",
        "values_kept": "Valores mantidos",
        "values_removed": "Valores removidos",
        "removed_values": "Valores removidos",
        "removed_value": "Valor removido",
        "column": "Coluna",
        "count": "Quantidade",
        "no_removed": "Nenhum valor foi removido.",
        "download": "Baixar TSV limpo",
        "download_name": "tsv_limpo.tsv",
        "missing_files": "Envie um arquivo TSV e um arquivo TXT para continuar.",
        "no_columns": "Selecione pelo menos uma coluna do TSV para limpar.",
        "empty_txt": "O arquivo TXT não contém valores utilizáveis.",
        "tsv_error": "Não foi possível ler o arquivo TSV.",
        "txt_error": "Não foi possível ler o arquivo TXT.",
        "success": "O arquivo TSV foi limpo com sucesso.",
        "detected_columns": "Colunas detectadas no TSV",
        "all_values": "Todos os valores autorizados",
    },
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def decode_uploaded_file(uploaded_file):
    """
    Decode an uploaded text file while supporting common encodings.
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

    raise UnicodeDecodeError(
        "unknown",
        raw_bytes,
        0,
        len(raw_bytes),
        "Unable to decode file",
    )


def read_tsv(uploaded_file):
    """
    Read a TSV as strings so that textual content is preserved.
    """
    text = decode_uploaded_file(uploaded_file)

    return pd.read_csv(
        io.StringIO(text),
        sep="\t",
        dtype=str,
        keep_default_na=False,
        na_filter=False,
    )


def normalize_value(
    value,
    ignore_case=True,
    ignore_accents=False,
    strip_whitespace=True,
):
    """
    Normalize a value for comparison only.

    The original spelling from the TSV is preserved in the output.
    """
    value = str(value)

    if strip_whitespace:
        value = value.strip()

    # Normalize repeated internal whitespace.
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


def parse_txt_values(text, format_option):
    """
    Parse the approved values from the TXT file.
    """
    if format_option == "lines":
        raw_values = text.splitlines()
    elif format_option == "pipe":
        raw_values = text.split("|")
    elif format_option == "comma":
        raw_values = text.split(",")
    elif format_option == "semicolon":
        raw_values = text.split(";")
    else:
        raw_values = text.splitlines()

    return [
        value.strip()
        for value in raw_values
        if value.strip()
    ]


def split_cell_values(cell, separator):
    """
    Split a TSV cell containing multiple values.
    """
    if cell is None:
        return []

    cell = str(cell)

    if not cell.strip():
        return []

    if separator == "":
        return [cell.strip()]

    return [
        value.strip()
        for value in cell.split(separator)
        if value.strip()
    ]


def clean_dataframe(
    dataframe,
    columns_to_clean,
    approved_normalized_values,
    cell_separator,
    ignore_case,
    ignore_accents,
    strip_whitespace,
):
    """
    Remove values from selected columns when their normalized forms
    are not present in the approved TXT list.
    """
    cleaned_df = dataframe.copy()

    removed_records = []

    stats = {
        "checked": 0,
        "kept": 0,
        "removed": 0,
    }

    for column in columns_to_clean:

        cleaned_column = []

        for cell in cleaned_df[column]:

            values = split_cell_values(
                cell=cell,
                separator=cell_separator,
            )

            kept_values = []

            for value in values:

                stats["checked"] += 1

                normalized = normalize_value(
                    value=value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                if normalized in approved_normalized_values:
                    kept_values.append(value)
                    stats["kept"] += 1

                else:
                    stats["removed"] += 1

                    removed_records.append(
                        {
                            "column": column,
                            "value": value,
                        }
                    )

            cleaned_cell = (
                f" {cell_separator} ".join(kept_values)
                if cell_separator
                else "".join(kept_values)
            )

            cleaned_column.append(cleaned_cell)

        cleaned_df[column] = cleaned_column

    return cleaned_df, removed_records, stats


def make_tsv_download(dataframe):
    """
    Convert a DataFrame to UTF-8 TSV bytes.
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
    options=["English", "Español", "Português"],
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
# PROCESS FILES
# ============================================================

if tsv_file is not None and txt_file is not None:

    # -------------------------
    # Read TSV
    # -------------------------

    try:
        df = read_tsv(tsv_file)

    except Exception as error:
        st.error(f"{t['tsv_error']} {error}")
        st.stop()

    # -------------------------
    # Read TXT
    # -------------------------

    try:
        txt_content = decode_uploaded_file(txt_file)

    except Exception as error:
        st.error(f"{t['txt_error']} {error}")
        st.stop()

    # -------------------------
    # Original preview
    # -------------------------

    st.subheader(t["preview_original"])

    st.dataframe(
        df.head(100),
        use_container_width=True,
    )

    st.caption(
        f"{t['detected_columns']}: "
        + " | ".join(str(column) for column in df.columns)
    )

    st.divider()


    # ========================================================
    # SETTINGS
    # ========================================================

    st.subheader(t["settings"])

    selected_columns = st.multiselect(
        t["select_columns"],
        options=list(df.columns),
        help=t["select_columns_help"],
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
            options=list(separator_options.keys()),
            index=0,
            help=t["separator_help"],
        )

        cell_separator = separator_options[
            selected_separator_label
        ]

        txt_format_labels = {
            t["txt_lines"]: "lines",
            t["txt_pipe"]: "pipe",
            t["txt_comma"]: "comma",
            t["txt_semicolon"]: "semicolon",
        }

        selected_txt_format_label = st.selectbox(
            t["txt_format"],
            options=list(txt_format_labels.keys()),
            index=0,
        )

        txt_format = txt_format_labels[
            selected_txt_format_label
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
    # PARSE APPROVED TXT VALUES
    # ========================================================

    approved_values = parse_txt_values(
        text=txt_content,
        format_option=txt_format,
    )

    # Remove duplicates while preserving original order.
    approved_values = list(dict.fromkeys(approved_values))

    if not approved_values:
        st.warning(t["empty_txt"])
        st.stop()

    approved_normalized_values = {
        normalize_value(
            value=value,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=strip_whitespace,
        )
        for value in approved_values
    }

    with st.expander(
        f"{t['preview_list']} — "
        f"{len(approved_values):,} {t['approved_values']}"
    ):
        approved_preview_df = pd.DataFrame(
            {
                t["all_values"]: approved_values
            }
        )

        st.dataframe(
            approved_preview_df,
            use_container_width=True,
            hide_index=True,
        )


    # ========================================================
    # CLEAN TSV
    # ========================================================

    if st.button(
        t["process"],
        type="primary",
        use_container_width=True,
    ):

        if not selected_columns:
            st.warning(t["no_columns"])
            st.stop()

        cleaned_df, removed_records, stats = clean_dataframe(
            dataframe=df,
            columns_to_clean=selected_columns,
            approved_normalized_values=approved_normalized_values,
            cell_separator=cell_separator,
            ignore_case=ignore_case,
            ignore_accents=ignore_accents,
            strip_whitespace=strip_whitespace,
        )

        st.success(t["success"])


        # ====================================================
        # RESULTS SUMMARY
        # ====================================================

        st.subheader(t["results"])

        metric_col1, metric_col2, metric_col3, metric_col4 = (
            st.columns(4)
        )

        metric_col1.metric(
            t["rows"],
            f"{len(cleaned_df):,}",
        )

        metric_col2.metric(
            t["values_checked"],
            f"{stats['checked']:,}",
        )

        metric_col3.metric(
            t["values_kept"],
            f"{stats['kept']:,}",
        )

        metric_col4.metric(
            t["values_removed"],
            f"{stats['removed']:,}",
        )


        # ====================================================
        # CLEANED FILE PREVIEW
        # ====================================================

        st.subheader(t["preview_cleaned"])

        st.dataframe(
            cleaned_df.head(100),
            use_container_width=True,
        )


        # ====================================================
        # REMOVED VALUE REPORT
        # ====================================================

        st.subheader(t["removed_values"])

        if removed_records:

            removed_df = pd.DataFrame(removed_records)

            removed_summary = (
                removed_df
                .groupby(
                    ["column", "value"],
                    dropna=False,
                )
                .size()
                .reset_index(name="count")
                .sort_values(
                    ["column", "count", "value"],
                    ascending=[True, False, True],
                )
                .rename(
                    columns={
                        "column": t["column"],
                        "value": t["removed_value"],
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
            st.info(t["no_removed"])


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
    st.info(t["missing_files"])
