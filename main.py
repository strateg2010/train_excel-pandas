import pandas as pd
from assets.functions import *


def get_product_info(product_id, frame, columns: list, ptype='parent', parent_code=None, child_list=None):
    """
    Функция генерирующая нужные данные из переданного фрейма в словарь.
    :param product_id: id товара
    :param frame: фрейм из которого берем данные
    :param columns: список колонок для составления словаря, для слияния итогового фрейма
    :param ptype: parent | child
    :param parent_code: Код товара родителя, нужен для дочерних товаров
    :param child_list: список дочерних (изначальный родитель в данном случае тоже является дочерней)
    :return: словарь для дальнейшей работы с фреймами
    """
    result = dict.fromkeys(columns)
    pname = frame['Товар'][product_id]
    attr_size = str(frame['Размер'][product_id])
    category = get_category(pname)
    if ptype == 'parent':
        result['Группы'] = category
        result['Тип'] = 'Товар'
        result['Код'] = frame['Код'][product_id]
        result['Наименование'] = pname
        result['Артикул'] = get_product_code(pname)
        result['Штрихкод EAN13'] = frame['Штрих-код'][product_id]
        result['Описание'] = frame['Состав'][product_id]
        result['Страна'] = frame['Страна'][product_id]
        result['Цена: Цена продажи'] = frame.iloc[product_id, 10]
        result['Валюта (Цена продажи)'] = 'б. руб'
        result['Закупочная цена'] = frame.iloc[product_id, 4]
        result['Валюта (Закупочная цена)'] = 'евро'
        if child_list:
            result['Остаток'] = sum(frame.iloc[i, 9] for i in child_list)
    if attr_size == '0':
        result['Остаток'] = frame.iloc[product_id, 9]

    if ptype == 'child':
        result['Тип'] = 'Модификация'
        result['Код товара модификации'] = parent_code
        result['Характеристика:Размер'] = frame['Размер'][product_id]
        result['Характеристика:Цвет'] = frame['Цвет'][product_id]

        main_cat, subcat = category.split('/')
        stop_list_subcat = ['Шарфы', 'Носки', 'Кепки', 'Костюмы', 'Комплекты', 'Накидки', 'Носки']

        if main_cat not in ['Бижутерия', 'Аксессуары', 'Обувь'] and subcat not in stop_list_subcat:
            if attr_size != 'nan':
                clothe_size = parse_clothe_size(category, attr_size)
                if category in ['Женщинам/Брюки', 'Женщинам/Шорты', 'Женщинам/Юбки']:
                    result['Характеристика:Обхват талии'] = clothe_size[0]
                    result['Характеристика:Обхват бёдер'] = clothe_size[1]
                elif main_cat == 'Мужчинам':
                    result['Характеристика:Обхват груди'] = clothe_size[0]
                    result['Характеристика:Обхват талии'] = clothe_size[1]
                else:
                    result['Характеристика:Обхват груди'] = clothe_size[0]
                    result['Характеристика:Обхват бёдер'] = clothe_size[1]

        result['Остаток'] = frame.iloc[product_id, 9]

    year_collections, type_collections = parse_seasons(str(frame['Сезон'][product_id]))
    result['Доп. поле: Год коллекции'] = year_collections
    result['Доп. поле: Сезон коллекции'] = type_collections
    result['Доп. поле: Страна производства'] = frame['Страна'][product_id]
    result['Доп. поле: Бренд'] = get_brand(pname)
    result = pd.DataFrame(result, index=[0])
    return result


def main():
    output_columns = [
        'Группы', 'Тип', 'Код', 'Наименование', 'Артикул', 'Цена: Цена продажи',
        'Валюта (Цена продажи)', 'Закупочная цена', 'Валюта (Закупочная цена)', 'Штрихкод EAN13', 'Описание',
        'Страна', 'Код товара модификации', 'Доп. поле: Год коллекции',
        'Доп. поле: Сезон коллекции', 'Доп. поле: Страна производства', 'Доп. поле: Бренд', 'Характеристика:Размер',
        'Характеристика:Цвет', 'Характеристика:Обхват груди', 'Характеристика:Обхват талии',
        'Характеристика:Обхват бёдер', 'Остаток'
    ]
    filenames = ['арена 2307', 'европа2307', 'метрополь', 'склад 2307']
    result_data = pd.DataFrame(columns=output_columns)
    for filename in filenames:
        df = pd.read_excel(f'datas/{filename}.xlsx', dtype='object')
        df.iloc[:, 10] = df.iloc[:, 10].astype('float64')
        # создание словаря с дублирующими артикулами
        data_dict = {}
        for row in range(df.index.max()):
            data_dict.setdefault(df['Код'][row], []).append(row)

        for pcode, ids_list in data_dict.items():
            parent_id = ids_list[0]
            check_attr = df['Размер'][parent_id]
            main_dict = get_product_info(parent_id, df, output_columns)
            result_data = result_data._append(main_dict, ignore_index=True)

            if check_attr != '0':
                for child_id in ids_list:
                    child_dict = get_product_info(child_id, df, output_columns, ptype='child', parent_code=pcode)
                    result_data = result_data._append(child_dict, ignore_index=True)

        outputfile = f'output_data/{filename}_export.xlsx'
        result_data.to_excel(outputfile, index=False)


if __name__ == '__main__':
    main()
