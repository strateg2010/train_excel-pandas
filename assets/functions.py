import re
import json
import pandas as pd


def get_brand(product_name: str) -> str:
    """
    Функция для получения производителя из наименования товара
    :param product_name: str - наименование товара
    :return: str - производитель
    """
    regex = re.compile(r'[A-Za-z.`]{3,15}')
    return ' '.join(re.findall(regex, product_name.replace('  ', ' ')))


def get_product_code(product_name: str) -> str:
    """
    Функция для получения кода товара из наименования товара
    :param product_name: str - наименование товара
    :return: str - код товара
    """
    try:
        regex = re.compile(r'(?:\w+\d+\W\w)?\S+\d+\S+')
        res = re.findall(regex, product_name.replace('  ', ' '))[0].strip()
    except IndexError:
        res = ''

    return res


def find_costume(product_name: str) -> str:
    regex = re.compile(r'^(.*)(?=костюм)')
    regex_del2 = re.compile(r'\([^.*]+\)')
    del_1 = re.sub(regex, '', product_name)
    del_2 = re.sub(regex_del2, ' ', del_1)
    return del_2.replace('  ', ' ')


def parse_seasons(season_code: str) -> tuple | str:
    """
    Функция парсинга (определения )
    :param season_code:
    :return:
    """
    if isinstance(season_code, int | float):
        raise TypeError('Сезонный код должен быть строкой')

    if '.' in season_code:
        season_code = season_code[2:] + season_code[:1]
    if season_code == '100':
        return ''

    season_year = '20' + season_code[:2]
    season_type = ('Осень-Зима', 'Весна-Лето')[int(season_code[-1]) % 2]
    return season_year, season_type


def get_category(product_name: str) -> str:
    """
    Функция парсинга категории из названия товара
    :param product_name: название товара
    :return: название категории
    """
    with open('assets/categories.json', 'r', encoding='u8') as file:
        categories = json.load(file)
    product_name = find_costume(product_name)
    for cat, query_list in categories.items():
        for query in query_list:
            if query in product_name:
                if (query in ['туфли', 'ботинки', 'сапоги'] and
                        any(i in product_name for i in ['туфли летние', 'полуботинки', 'полусапоги'])):
                    continue
                return cat


def parse_clothe_size(product_category: str, product_size: str) -> tuple[str]:
    """
    Функция для нахождения размеров одежды для разных полов
    :param product_category: Полное название категории
    :param product_size: Размер одежды
    :return: (грудь|талия, бедра)
    """
    sex, cat = product_category.split('/')
    regex = re.compile(r'\d+')
    product_size = regex.findall(product_size)

    if product_size:
        sizes_df = pd.read_excel('assets/sizes_data.xlsx',
                                 sheet_name=sex, dtype=str)
        sizes_df.set_index('Категория', inplace=True)
        return tuple(sizes_df.loc[cat, int(product_size[0])].split('|'))

