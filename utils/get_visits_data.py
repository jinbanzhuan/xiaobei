import csv
import os


def get_csv_visits_data():
    """读取CSV文件返回测试数据，处理空值"""
    test_data = []
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'visits_data.csv')

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 将空字符串转换为 None 或保持空字符串
            contents = row['contents'].strip() if row['contents'] else ""
            sourceDepartments = row['sourceDepartments'].strip() if row['sourceDepartments'] else ""
            sourcePersons = row['sourcePersons'].strip() if row['sourcePersons'] else ""

            test_data.append((
                contents,
                sourceDepartments,
                sourcePersons,
            ))
    return test_data