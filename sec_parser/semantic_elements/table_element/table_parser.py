from __future__ import annotations

from io import StringIO

import pandas as pd


class TableParser:
    def __init__(self, html: str) -> None:
        self._html = html

    @staticmethod
    def _basic_preprocessing(html: str) -> pd.DataFrame:
        if not isinstance(html, pd.DataFrame):
            tables = pd.read_html(StringIO(html), flavor="lxml")
            if len(tables) == 0:
                msg = "No tables found"
                raise ValueError(msg)
            table = tables[0]
        else:
            table = html
        table = table.dropna(how="all")
        table.columns = pd.Index(table.iloc[0].tolist())
        table = table[1:]
        table = table.dropna(axis=1, how="all")
        first_row = list(table.columns)
        new_df = pd.DataFrame([first_row], columns=table.columns)
        table = pd.concat([new_df, table], ignore_index=True)
        table.columns = pd.Index(
            list(range(1, len(table.columns) + 1)),
            dtype=str,
        )
        table = table.fillna("")
        return table.astype(str)

    @staticmethod
    def _remove_blank_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns_to_remove = []
        for i, _ in enumerate(df.columns):
            if i < len(df.columns) - 1:
                current_column = df.columns[i]
                next_column = df.columns[i + 1]
                non_empty_rows = df[
                    (df[current_column] != "") & (df[next_column] != "")
                ]
                if (
                    non_empty_rows[current_column] == non_empty_rows[next_column]
                ).all():
                    if (df[current_column] == "").sum() >= (
                        df[next_column] == ""
                    ).sum():
                        columns_to_remove.append(current_column)
                    else:
                        columns_to_remove.append(next_column)
        return df.drop(columns=columns_to_remove)

    @staticmethod
    def _merge_columns_by_marker(table: pd.DataFrame, marker: str) -> pd.DataFrame:
        for i, _ in enumerate(table.columns):
            if i < len(table.columns) - 1:
                current_column = table.columns[i]
                next_column = table.columns[i + 1]
                non_marker_rows = table[
                    (table[current_column] != marker) & (table[next_column] != marker)
                ]
                non_empty_non_marker_rows = non_marker_rows[
                    (non_marker_rows[current_column] != "")
                    & (non_marker_rows[next_column] != "")
                ]
                marker_rows = table.drop(non_empty_non_marker_rows.index)
                marker_rows_indices = marker_rows.index
                if (
                    non_empty_non_marker_rows[current_column]
                    == non_empty_non_marker_rows[next_column]
                ).all():
                    table.loc[marker_rows_indices, current_column] = (
                        table.loc[marker_rows_indices, current_column]
                        .str.cat(
                            table.loc[marker_rows_indices, next_column],
                            sep="",
                            na_rep="",
                        )
                        .str.strip()
                    )
                    table = table.drop(columns=[next_column])
        return table

    def parse_as_df(self) -> pd.DataFrame:
        table = self._basic_preprocessing(self._html)
        table = self._remove_blank_columns(table)
        table = self._merge_columns_by_marker(table, "$")
        table = self._merge_columns_by_marker(table, "%")
        table.columns = pd.Index(
            list(range(1, len(table.columns) + 1)),
            dtype=str,
        )
        return table
