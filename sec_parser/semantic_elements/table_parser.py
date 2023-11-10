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
        df=df.astype(str)
        return df

    @staticmethod
    def remove_blank_columns(df: pd.DataFrame) -> pd.DataFrame:
        columns_to_remove = []
        for i in range(len(df.columns)):
            if i < len(df.columns)-1:
                col1 = df.columns[i]
                col2 = df.columns[i + 1]
                non_empty_rows = df[(df[col1] != '') & (df[col2] != '')]
                if (non_empty_rows[col1] == non_empty_rows[col2]).all():
                    if (df[col1] == '').sum() >= (df[col2] == '').sum():
                        columns_to_remove.append(col1)
                    else:
                        columns_to_remove.append(col2)
        df.drop(columns=columns_to_remove, inplace=True)
        return df
    @staticmethod

    def merge_dollar_columns(df: pd.DataFrame) -> pd.DataFrame:
        for i in range(len(df.columns)):
            if i < len(df.columns)-1:
                col1 = df.columns[i]
                col2 = df.columns[i + 1]
                non_dollar_rows = df[(df[col1] != '$') & (df[col2] != '$')]
                non_dollar_rows=non_dollar_rows[(non_dollar_rows[col1] != '') & (non_dollar_rows[col2] != '')]
                dollar_rows=df.drop(non_dollar_rows.index)
                dollar_rows_indices=dollar_rows.index
                if (non_dollar_rows[col1] == non_dollar_rows[col2]).all():
                    df.loc[dollar_rows_indices, col1] = df.loc[dollar_rows_indices, col1].str.cat(df.loc[dollar_rows_indices, col2], sep='', na_rep='').str.strip()
                    df.drop(columns=[col2], inplace=True)
        return df
    
    @staticmethod
    def merge_percentage_columns(df: pd.DataFrame) -> pd.DataFrame:
        for i in range(len(df.columns)):
            if i < len(df.columns)-1:
                col1 = df.columns[i]
                col2 = df.columns[i + 1]
                non_dollar_rows = df[(df[col1] != '%') & (df[col2] != '%')]
                non_percentage_rows=non_dollar_rows[(non_dollar_rows[col1] != '') & (non_dollar_rows[col2] != '')]
                percentage_rows=df.drop(non_percentage_rows.index)
                percentage_rows_indices=percentage_rows.index
                if (non_percentage_rows[col1] == non_percentage_rows[col2]).all():
                    df.loc[percentage_rows_indices, col1] = df.loc[percentage_rows_indices, col1].str.cat(df.loc[percentage_rows_indices, col2], sep='', na_rep='').str.strip()
                    df.drop(columns=[col2], inplace=True)
        return df
    
    def parse(self) -> pd.DataFrame:
        soup = self.table_element.html_tag.get_source_code()
        df = self.basic_preprocessing(soup)
        df = self.remove_blank_columns(df)
        df = self.merge_dollar_columns(df)
        df = self.merge_percentage_columns(df)
        df.columns = range(1, len(df.columns) + 1)
        self.df=df
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
