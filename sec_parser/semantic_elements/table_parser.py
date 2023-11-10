import pandas as pd
from bs4 import BeautifulSoup
from typing import Any
from sec_parser.semantic_elements.table_element import TableElement

class TableParser:
    def __init__(self, table_element: 'TableElement'):
        self.table_element = table_element
        self.df = None

    @staticmethod
    def basic_preprocessing(soup: BeautifulSoup) -> pd.DataFrame:
        df = pd.read_html(str(soup))[0]
        df = df.dropna(how='all')
        df.columns = df.iloc[0]
        df = df[1:]
        df = df.dropna(axis=1, how='all')
        first_row = [col for col in df.columns]
        new_df = pd.DataFrame([first_row], columns=df.columns)
        df = pd.concat([new_df, df], ignore_index=True)
        df.columns = range(1, len(df.columns) + 1)
        df = df.fillna('')
        df = df.astype(str)
        return df

    @staticmethod
    def remove_blank_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns_to_remove = []
        for i in range(len(df.columns)):
            if i < len(df.columns)-1:
                current_column = df.columns[i]
                next_column = df.columns[i + 1]
                non_empty_rows = df[(df[current_column] != '') & (df[next_column] != '')]
                if (non_empty_rows[current_column] == non_empty_rows[next_column]).all():
                    if (df[current_column] == '').sum() >= (df[next_column] == '').sum():
                        columns_to_remove.append(current_column)
                    else:
                        columns_to_remove.append(next_column)
        df.drop(columns=columns_to_remove, inplace=True)
        return df
    @staticmethod
    def merge_columns_by_marker(df: pd.DataFrame, marker: str) -> pd.DataFrame:
        for i in range(len(df.columns)):
            if i < len(df.columns)-1:
                current_column = df.columns[i]
                next_column = df.columns[i + 1]
                non_marker_rows = df[(df[current_column] != marker) & (df[next_column] != marker)]
                non_empty_non_marker_rows = non_marker_rows[(non_marker_rows[current_column] != '') & (non_marker_rows[next_column] != '')]
                marker_rows = df.drop(non_empty_non_marker_rows.index)
                marker_rows_indices = marker_rows.index
                if (non_empty_non_marker_rows[current_column] == non_empty_non_marker_rows[next_column]).all():
                    df.loc[marker_rows_indices, current_column] = (df.loc[marker_rows_indices, current_column]
                                                                   .str.cat(df.loc[marker_rows_indices, next_column], sep='', na_rep='')
                                                                   .str.strip())
                    df.drop(columns=[next_column], inplace=True)
        return df

    def parse(self) -> 'TableParser':
        soup = self.table_element.html_tag.get_source_code()
        df = self.basic_preprocessing(soup)
        df = self.remove_blank_columns(df)
        df = self.merge_columns_by_marker(df, '$')
        df = self.merge_columns_by_marker(df, '%')
        df.columns = range(1, len(df.columns) + 1)
        self.df = df
        return self

    def table_as_df(self) -> pd.DataFrame:
        if self.df is not None:
            return self.df
        else:
            raise ValueError("DataFrame 'self.df' has not been initialized. Please call 'parse' method first.")

    def table_as_json(self) -> dict[str, Any]:
        if self.df is not None:
            return self.df.to_json(orient="split")
        else:
            raise ValueError("DataFrame 'self.df' has not been initialized. Please call 'parse' method first.")
