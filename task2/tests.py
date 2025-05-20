import os
import asyncio

import pandas as pd

from task2.solution import main


def test_main():
    csv_filename = 'test_beasts.csv'
    WIKIPEDIA_PROVIDED_CNT = 47295
    OK_EXISTING_PERCENT = 0.85
    asyncio.run(main(csv_filename))
    
    file_path = os.path.dirname(__file__) + "/" + csv_filename

    # Проверяем, что файл существует
    assert os.path.exists(file_path) is True

    with open(file_path, 'r', encoding='utf-8') as file:
        df = pd.read_csv(file)
        
        # Проверяем, что корректность названий колонок
        assert list(df.columns) == ['Unnamed: 0', 'Animal first letter', 'count']

        all_data: list[tuple[str, int]] = [(letter, count) for letter, count in zip(df['Animal first letter'], df['count'])]

        # Проверяем, что длина строки в первой колонки равна 1
        assert all(len(data[0]) == 1 for data in all_data) is True

        # Проверяем, что общее количество животных больше 90% от количества, указанного в Wikipedia
        assert sum([data[1] for data in all_data]) >= WIKIPEDIA_PROVIDED_CNT * OK_EXISTING_PERCENT
    
    try:
        os.remove(file_path)
    except Exception:
        pass
