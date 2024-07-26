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
    if ptype == 'parent':
        result['Группы'] = get_category(pname)
        result['Тип'] = 'Товар'
        result['Код'] = frame['Код'][product_id]
        result['Наименование'] = pname
        result['Артикул'] = get_product_code(pname)
        result['Штрихкод EAN13'] = frame['Штрих-код'][product_id]
        result['Описание'] = frame['Состав'][product_id]
        result['Страна'] = frame['Страна'][product_id]
        if child_list:
            result['Остаток'] = sum(frame.iloc[i, 9] for i in child_list)
    elif ptype == 'child':
        result['Тип'] = 'Модификация'
        result['Код товара модификации'] = parent_code
        result['Характеристика:Размер'] = frame['Размер'][product_id]
        result['Характеристика:Цвет'] = frame['Цвет'][product_id]
        result['Остаток'] = frame.iloc[product_id, 9]

    result['Цена: Цена продажи'] = frame.iloc[product_id, 10]
    result['Валюта (Цена продажи)'] = 'б. руб'
    result['Закупочная цена'] = frame.iloc[product_id, 4]
    result['Валюта (Закупочная цена)'] = 'евро'
    year_collections, type_collections = parse_seasons(str(frame['Сезон'][product_id]))
    result['Доп. поле: Год коллекции'] = year_collections
    result['Доп. поле: Сезон коллекции'] = type_collections
    result['Доп. поле: Страна производства'] = frame['Страна'][product_id]
    result['Доп. поле: Бренд'] = get_brand(pname)

    return result


def main():
    output_columns = [
        'Группы', 'Тип', 'Код', 'Наименование', 'Артикул', 'Цена: Цена продажи',
        'Валюта (Цена продажи)', 'Закупочная цена', 'Валюта (Закупочная цена)', 'Штрихкод EAN13', 'Описание',
        'Страна', 'Код товара модификации', 'Доп. поле: Год коллекции',
        'Доп. поле: Сезон коллекции', 'Доп. поле: Страна производства', 'Доп. поле: Бренд', 'Характеристика:Размер',
        'Характеристика:Цвет', 'Остаток'
        # 'Минимальная цена', 'Валюта (Минимальная цена)', (до Страны)
    ]
    filename = 'datas/склад 2307.xlsx'
    df = pd.read_excel(filename, dtype='object')
    df.iloc[:, 10] = df.iloc[:, 10].astype('float64')
    result_data = pd.DataFrame(columns=output_columns)
    # создание словаря с дублирующими артикулами
    data_dict = {}
    for row in range(df.index.max()):
        data_dict.setdefault(df['Код'][row], []).append(row)

    for pcode, ids_list in data_dict.items():
        parent_id = ids_list[0]
        main_dict = get_product_info(parent_id, df, output_columns, child_list=ids_list)
        result_data = result_data._append(main_dict, ignore_index=True)

        for child_id in ids_list:
            child_dict = get_product_info(child_id, df, output_columns, ptype='child', parent_code=pcode)
            result_data = result_data._append(child_dict, ignore_index=True)

    outputfile = filename[:filename.rfind('.')] + '_export' + filename[filename.rfind('.'):]
    new_path = 'output_data' + outputfile[outputfile.find('/'):]
    result_data.to_excel(new_path, index=False)


if __name__ == '__main__':
    main()
