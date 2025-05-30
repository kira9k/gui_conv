import pandas as pd
from typing import List, Tuple


class ParseFiles:

    @staticmethod
    def pars_dtx_spectr(test_path: str, column_names: List, skiprows: int):
        """Парсер для спектра
        Парсит ОДИН .dtx файл со значениями спектра 

        Args:
            test_path (str): путь до файла
            column_names (List): названия столбцов для каждой колонки
            skiprows (int): сколько строк пропустить

        Returns:
            df(DataFrame): таблица со всеми параметрами спектра
        """
        df = pd.read_csv(test_path,
                         header=None,
                         sep='\t',
                         skiprows=skiprows,
                         decimal=',')

        df.replace('No data', pd.NA, inplace=True)

        df.columns = column_names

        for col in df.columns[1:]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        return df
    
    
