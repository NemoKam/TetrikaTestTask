# Необходимо реализовать скрипт, который будет получать с русскоязычной википедии список всех животных
# (https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту) и записывать в файл в формате beasts.csv
# количество животных на каждую букву алфавита. Содержимое результирующего файла:

import asyncio
import os
import pandas as pd
from collections import defaultdict

import aiohttp
from aiohttp import ClientSession

from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.limit_per_page: int = 200
        self._session: ClientSession | None = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, *args):
        await self._session.close()

    async def get_soup_from_url(self, url: str) -> BeautifulSoup:
        async with self._session.get(url) as resp:
            return BeautifulSoup(await resp.text(), "html.parser")

    async def get_animals_info(self, base_url: str, start: str, end: str | None = None) -> dict[str, int] | tuple[str, str | None, str]:
        soup: BeautifulSoup = await self.get_soup_from_url(base_url + "?pagefrom=" + start)
        animals: list[str] = []
        info: defaultdict[str, int] = defaultdict(int)

        mv_pages: BeautifulSoup = soup.find("div", {"id": "mw-pages"})
        if mv_pages is None:
            return info
        
        animals: list[str] = [str(li.text).upper() for li in mv_pages.find("div", {"class": "mw-category-group"}).find_all("li")
                              if start <= str(li.text).upper() and (end is None or str(li.text).upper() < str(end))]
        # Проверка start <= str(li.text) нужна для того, чтобы не брать животных другого алфавита, так как
        # Животные идут от А до Я, A до Z, а так как буквы "русские" > "английских", то сравниваем их как строки
        # Сравнение str(li.text) < str(end) лишь для исключения животных, которые начинаются на буквы, которые идут начиная с end

        print(start, end, len(animals))

        if len(animals) >= self.limit_per_page:
            return (start, end)
        
        for animal in animals:
            # Пример: Амбициозный зверь (start=А, end=АМ) max(len(A), len(AM)) = 2 => animal_prefix = Am
            animal_prefix = animal[:max(len(start), len(str(end)))]
            info[animal_prefix] += 1

        return info

    async def get_categories_alphabet_count(self, symbols: str) -> defaultdict[str, int]:
        BASE_URL: str = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"
        
        animals_data: defaultdict[str, int] = defaultdict(int)
        symbols_indexes: defaultdict[str, int] = defaultdict(int)
        # Сохраняем индексы букв для последующего быстрого получения
        for i, symbol in enumerate(symbols):
            symbols_indexes[symbol] = i

        queries: list[tuple[str, str | None]] = [(symbols[i], symbols[i + 1] if i + 1 < len(symbols) else None,)
                                                for i in range(len(symbols))]
        while len(queries) > 0:
            results: list[defaultdict[str, int] | tuple[str, str | None]] = await asyncio.gather(*[self.get_animals_info(BASE_URL, *query) for query in queries])
            queries.clear()

            for result in results:
                if isinstance(result, tuple):
                    new_queries: list[tuple[int, int | None]] = []
                    start, end = result

                    # ------------------------------------------------------------------------
                    # Можно придумать алгоритм ускорения. Например, если при start=О, end=П
                    # встречаются много начинающихся на "ОБЫКНОВЕНН", и можно сразу его взять,
                    # а не по 1 букве доходить до него.
                    # ------------------------------------------------------------------------

                    first_last_symbol = start[-1]
                    end_last_symbol = end[-1] if end is not None else symbols[-1]
                    # Базовая логика формирования новых запросов:
                    # Пример: start=А, end=Б
                    # Запросы:
                    #   1) start=А, end=АА
                    #   2) start=АА, end=АЯ
                    #   3) start=АЯ, end=Б
                    new_queries += [(start, start + symbols[0]),
                                    (start + symbols[0], start + symbols[-1]),
                                    (start + symbols[-1], end)]
                    
                    # Если же начиются одинаково start=...X, end=...Y Пример: start=АББА, end=АББZ
                    # Если не дошло до одного из моментов:
                    #   * start=...А, end=...Б
                    #   * start=...Ю, end=...Z
                    # При таких моментах логика формирования запросов базовая.
                    if len(start) > 1 and (end is None or len(start) == len(str(end))) \
                        and symbols_indexes[first_last_symbol] + 1 < symbols_indexes[end_last_symbol] \
                        and end_last_symbol != symbols[1] and first_last_symbol != symbols[-1]:
                        # Запросы (Берем среднюю букву между X и Y):
                        #   1) start=АА, end=АО
                        #   2) start=АО, end=АЯ
                        mid_symbol_index = (symbols_indexes[first_last_symbol] + symbols_indexes[end_last_symbol]) // 2
                        mid = start[:-1] + symbols[mid_symbol_index]
                        new_queries[0] = (start, mid)
                        new_queries[1] = (mid, end)
                        new_queries.pop(-1)

                    queries += new_queries

                elif isinstance(result, defaultdict):
                    # Достаем из словаря все префиксы животных с их количеством и добавляем в общий список
                    # Пример:
                    #   {
                    #       "АББА": 10,
                    #       "АББУ": 12,
                    #       ...
                    #   }
                    for animal_prefix, animal_count in result.items():
                        animals_data[animal_prefix] += animal_count
                        print(animal_prefix, animal_count)

        return animals_data
    
    async def get_categories_count(self) -> defaultdict[str, int]:
        RU_SYMBOLS: str = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ".replace("Ё", "")
        EN_SYMBOLS: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        animals_data: defaultdict[str, int] = defaultdict(int)

        results: list[defaultdict[str, int]] = await asyncio.gather(
            self.get_categories_alphabet_count(RU_SYMBOLS),
            self.get_categories_alphabet_count(EN_SYMBOLS)
        )

        for result in results:
            animals_data.update(result)
        
        return animals_data


async def main(csv_filename: str):
    async with Scraper() as scraper:
        animals_data: defaultdict[str, int] = await scraper.get_categories_count()
    
    # Остается только обьединить количество ключей по первой букве
    letters_data: defaultdict[str, int] = defaultdict(int)
    for animal_prefix, animal_count in animals_data.items():
        print(animal_prefix[0], animal_prefix, animal_count)
        letters_data[animal_prefix[0]] += animal_count
    
    # Конвертируем из словаря в обычный массив для удобного переноса в pandas
    converted_result_list: list[tuple[str, int]] = [(letter, count) for letter, count in letters_data.items()]
    converted_result_list.sort(key=lambda animal_info: animal_info[0]) # Сортируем по букве в алфавитном порядке
    
    df = pd.DataFrame(
        {
            "Animal first letter": [letter for letter in letters_data],
            "count": [animal_count for animal_count in letters_data.values()]
        }
    ).sort_values(by="Animal first letter")

    file_path = os.path.dirname(__file__) + "/" + csv_filename

    df.to_csv(file_path, encoding="utf-8")

    # Готово! Вывело в сумме 44626 из Wikipedia пишет: "47 295, находящихся в данной категории. Список ниже может не отражать последних изменений".

if __name__ == "__main__":
    asyncio.run(main("beasts.csv"))
