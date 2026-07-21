import os
import csv


def get_csv_visits_item_data():
    test_data = []
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'visits_item_data.csv')
    with open(csv_path, 'r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question = row['question']
            test_data.append(question)
    return test_data