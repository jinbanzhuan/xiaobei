import os
import csv


def get_csv_queries_data():
    """读取 data/queries_data.csv，返回 question 字符串列表。

    数据来源：~/Desktop/queries.jsonl 中的 question 字段（脱去换行）。
    风格与 get_csv_visits_item_data 一致，用于原生小北 chat 批量灌参。
    """
    test_data = []
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'queries_data.csv')
    with open(csv_path, 'r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row['question']
            test_data.append(question)
    return test_data
