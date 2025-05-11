from __future__ import annotations

import math
from typing import List

import pandas as pd
import streamlit as st

from .validate import normalize_text


def split_frame(df: pd.DataFrame, batch_size: int) -> List[pd.DataFrame]:
    """
    Split a Pandas DataFrame into smaller DataFrames of a specified batch size.

    Args:
        df (pd.DataFrame): The input DataFrame to be split.
        batch_size (int): The number of rows per batch.

    Returns:
        List[pd.DataFrame]: A list of DataFrames, each containing at most `batch_size` rows.
    """
    return [df[i : i + batch_size] for i in range(0, len(df), batch_size)]


def filter_dataframe(df: pd.DataFrame, user_session: dict) -> pd.DataFrame:
    """
    Filter a DataFrame based on user-selected columns and search criteria.

    This function creates an interactive interface for users to select columns
    and enter search terms. It then filters the DataFrame based on these inputs.

    Args:
        df (pd.DataFrame): The input DataFrame to be filtered.

    Returns:
        pd.DataFrame: A filtered version of the input DataFrame based on user inputs.

    Note:
        This function uses Streamlit for creating the interactive interface and
        stores filter states in Streamlit's session state.
    """
    df = df.copy()

    # normalize_text
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str)

    with st.expander("🔍 **Advanced filter**", expanded=True):
        col_input, _ = st.columns([1, 1])
        with col_input:
            to_filter_columns = st.multiselect("Select column to filter", df.columns)

        user_session["filters"] = {}

        for column in to_filter_columns:
            col_input, _ = st.columns([1, 1])
            with col_input:
                if df[column].dtype == object:
                    user_session["filters"][column] = st.text_input(
                        f"🔠 Search in **{column}** (Regex is supported)",
                        value=user_session["filters"].get(column, ""),
                        placeholder="Enter keyword or regex...",
                    )

        # search
        if st.button("🔍 **Search**"):
            user_session["search_clicked"] = True
            user_session["filter_expanded"] = True
            st.rerun()

    # View result after search
    if user_session.get("search_clicked", False):
        for column, value in user_session["filters"].items():
            if isinstance(value, str) and value:
                df = df[
                    df[column]
                    .astype(str)
                    .apply(normalize_text)
                    .str.contains(normalize_text(value), na=False)
                ]

    return df


def paginate_df(
    name: str, dataset, streamlit_object: str, disabled=None, num_rows=None
):
    """
    Create a paginated display of a dataset using Streamlit components.

    This function provides an interactive interface for viewing and sorting a dataset,
    with options for pagination and sorting.

    Args:
        name (str): A unique identifier for the Streamlit components.
        dataset: The dataset to be displayed (expected to be a pandas DataFrame).
        streamlit_object (str): The type of Streamlit object to use for display.
            Can be either 'df' for a regular dataframe or 'editable df' for an editable one.
        disabled (list, optional): A list of columns to be disabled in the editable dataframe.
            Only used when streamlit_object is 'editable df'. Defaults to None.
        num_rows (int, optional): The number of rows to display in the editable dataframe.
            Only used when streamlit_object is 'editable df'. Defaults to None.

    Returns:
        None: This function doesn't return a value, it displays the paginated dataset
        directly in the Streamlit app.

    Note:
        This function uses various Streamlit components (st.warning, st.expander, st.columns, etc.)
        and assumes that the 'st' object is available in the global namespace.
    """
    if dataset.empty:
        st.warning("⚠️ No data to display.")
        return

    pagination = st.container()
    bottom_menu = st.columns((4, 1, 1))

    with bottom_menu[2]:
        batch_size = st.selectbox(
            "📏 **Page sizes**", options=[10, 25, 50, 100], key=f"{name}"
        )

    total_pages = max(math.ceil(len(dataset) / batch_size), 1)

    with bottom_menu[1]:
        current_page = st.number_input(
            "📌 **Page**",
            min_value=1,
            max_value=total_pages,
            step=1,
            value=1,
        )

    with bottom_menu[0]:
        st.markdown(f"📖 Page **{current_page}** on **{total_pages}** ")

    pages = split_frame(dataset, batch_size)

    if current_page <= len(pages):
        if streamlit_object == "df":
            pagination.dataframe(
                pages[current_page - 1], hide_index=True, use_container_width=True
            )
        elif streamlit_object == "editable df":
            pagination.data_editor(
                pages[current_page - 1],
                hide_index=True,
                disabled=False if disabled is None else disabled,
                num_rows=num_rows,  # type: ignore
                use_container_width=True,
            )  # type: ignore
    else:
        st.warning("⚠️ Page number exceeds the valid range.")
