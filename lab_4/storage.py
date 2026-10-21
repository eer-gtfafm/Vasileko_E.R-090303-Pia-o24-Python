import csv
import json
import os
from models import Movie


def load_movies_from_json():
    """загрузка списка фильмов из JSON"""
    if not os.path.exists("data.json"):
        return []  # если файла нет (первый запуск), возвращаем пустой список
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            dict_list = json.load(file)
            return [Movie.from_dict(item) for item in dict_list] # переводим словари обратно в объекты классов
    except Exception:
        print("ошибка при чтении файла JSON, создан пустой список.")
        return []


def save_movies_to_json(movies_list):
    """сохранение списка фильмов в JSON"""
    dict_list = [m.to_dict() for m in movies_list] # переводим список объектов классов в список обычных словарей
    with open("data.json", "w", encoding="utf-8") as file:
        json.dump(dict_list, file, ensure_ascii=False, indent=4)


def export_to_csv(movies_list):
    """экспорт данных в формат CSV таблицы"""
    with open("data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file) 
        writer.writerow(["Название", "Жанр", "Год", "Рейтинг"]) # пишем шапку таблицы
        for m in movies_list:
            writer.writerow([m.name, m.genre, m.year, m.rating])
