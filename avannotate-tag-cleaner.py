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

    1. Entity category:
       Determines whether an ORIGINAL TSV value belongs to
       People, Organizations, or Places.

    2. Preferred TXT spelling:
       Uses the spelling found in the TXT category list.

    3. Modifications:
       Applied ONLY AFTER the value has:
       - been categorized,
       - moved to the correct TSV column if necessary, and
       - confirmed as present in one of the TXT category lists.

    Processing order:
        ORIGINAL TSV VALUE
            ↓
        CATEGORY LOOKUP
            ↓
        MOVE TO CORRECT COLUMN
            ↓
        DELETE IF NOT IN TXT CATEGORY LISTS
            ↓
        APPLY MODIFICATION
    """

    category_lookup = {}
    preferred_spelling_lookup = {}

    # --------------------------------------------------------
    # Build category lookup from the three approved TXT lists.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Build modification lookup separately.
    #
    # These rules DO NOT determine whether a value is valid
    # and DO NOT determine its entity category.
    # --------------------------------------------------------

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
    Process the TSV in this exact order:

    STEP 1 — REORGANIZE
        Examine each ORIGINAL TSV value.
        If it appears in the TXT People, Organizations, or Places
        list, assign it to that TXT category and therefore to the
        corresponding TSV column.

    STEP 2 — DELETE
        If the ORIGINAL TSV value does not appear in any of the
        three TXT category lists, remove it.

    STEP 3 — MODIFY
        After a surviving value has been placed in the correct
        TSV column, apply any matching TXT modification rule:

            old value -> new value

    Important:
        A modification rule does not rescue a value that is absent
        from the TXT People, Organizations, and Places lists.

        Example:

            TXT Places:
                Mexico

            TXT Modifications:
                Méjico -> México

        If the TSV contains "Méjico" but "Méjico" itself does not
        occur in one of the three TXT category lists, it will be
        deleted before the modification stage.

        To retain and then modify it, the TXT should contain:

            Places
            Méjico

            Modifications
            Méjico -> México
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
    # Process each TSV row independently.
    # --------------------------------------------------------

    for row_index in cleaned_df.index:

        # Values are rebuilt into their correct entity columns.
        row_output = {
            "people": [],
            "organizations": [],
            "places": [],
        }

        # ----------------------------------------------------
        # Read values from all three original TSV entity columns.
        # ----------------------------------------------------

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

                # ==================================================
                # STEP 1:
                # IDENTIFY THE CATEGORY OF THE ORIGINAL TSV VALUE
                # ==================================================

                normalized_original = normalize_value(
                    original_value,
                    ignore_case=ignore_case,
                    ignore_accents=ignore_accents,
                    strip_whitespace=strip_whitespace,
                )

                destination_category = category_lookup.get(
                    normalized_original
                )

                # ==================================================
                # STEP 2:
                # DELETE VALUES ABSENT FROM ALL TXT CATEGORY LISTS
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

                # --------------------------------------------------
                # Use the preferred spelling from the TXT category
                # list before applying any modification.
                # --------------------------------------------------

                categorized_value = preferred_spelling_lookup.get(
                    normalized_original,
                    original_value,
                )

                # --------------------------------------------------
                # Record whether the approved value remained in its
                # original category or moved to another TSV column.
                # --------------------------------------------------

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
                # APPLY MODIFICATIONS ONLY AFTER CATEGORY VALIDATION
                # AND REORGANIZATION
                # ==================================================

                normalized_categorized_value = normalize_value(
                    categorized_value,
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

                # --------------------------------------------------
                # Add the final value to the category determined
                # BEFORE modification.
                #
                # The modification itself does not change category.
                # --------------------------------------------------

                row_output[
                    destination_category
                ].append(final_value)

        # ----------------------------------------------------
        # Replace the three original entity cells with the
        # reorganized, cleaned, and modified values.
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
