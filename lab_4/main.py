from exceptions import InvalidRatingError
import services
from storage import export_to_csv, load_movies_from_json, save_movies_to_json


def get_num_input(prompt, is_float=False): # проверка на воод числа
    while True:
        try:
            return float(input(prompt)) if is_float else int(input(prompt))
        except ValueError:
            print("ошибка. введите числовое значение!")


def main():
    movies = load_movies_from_json()  # при старте автоматически загружаем ранее сохраненные фильмы
    while True:
        print("\n===== МЕНЮ КАТАЛОГА ФИЛЬМОВ =====")
        print("1. добавить фильм")
        print("2. показать все фильмы")
        print("3. найти фильмы по жанру")
        print("4. фильтрация по рейтингу")
        print("5. сортировка по рейтингу")
        print("6. показать статистику рейтингов")
        print("7. экспортировать в CSV")
        print("8. удалить фильм")
        print("0. выход")
        choice = input("выберите действие: ").strip()
        if choice == "1":
            name_i = input("введите название фильма: ").strip()
            genre_i = input("введите жанр фильма: ").strip()
            while True:
                try:
                    year_i = int(input("введите год выпуска: "))
                    if year_i < 1895 or year_i > 2026:
                        print("в этом году нет фильмов :( попробуйте другой:")
                        continue
                    break
                except ValueError:
                    print("введите год целым числом!")
            while True:
                try:
                    rating_i = float(input("введите рейтинг (0-10): ")) # передаем данные в функции/классы — там сработает raise, если рейтинг неверный
                    from models import Movie
                    new_movie = Movie(name_i, genre_i, year_i, rating_i)
                    movies.append(new_movie)
                    save_movies_to_json(movies)  # сразу сохраняем на диск в JSON
                    print(f"фильм '{name_i}' успешно добавлен и сохранен!")
                    break
                except InvalidRatingError as e: # ловим наше собственное исключение 
                    print(f"ошибка (сработало исключение): {e}")
                except ValueError:
                    print("введите число!")
        elif choice == "2":
            if not movies:
                print("каталог фильмов пока пуст :(")
                continue
            print("\nсписок всех фильмов:")
            for idx, m in enumerate(movies, 1):
                print(f"{idx}. {m}")
        elif choice == "3":
            g = input("введите жанр для поиска: ").strip()
            found = services.search_by_genre(movies, g)
            if found:
                print(f"\nнайденные фильмы в жанре '{g}':")
                for m in found:
                    print(f"- {m}")
            else:
                print(f"фильмы в жанре '{g}' не найдены")
        elif choice == "4":
            r = get_num_input("показать фильмы с рейтингом не ниже: ", is_float=True)
            filtered = services.filter_by_rating(movies, r)
            if filtered:
                print(f"\nфильмы с рейтингом >= {r}:")
                for m in filtered:
                    print(f"- {m}")
            else:
                print("подходящие фильмы отсутствуют")
        elif choice == "5":
            if not movies:
                print("каталог пуст.")
                continue
            sorted_list = services.sort_movies_by_rating(movies)
            print("\nфильмы, отсортированные по убыванию рейтинга:")
            for m in sorted_list:
                print(f"- {m}")
        elif choice == "6":
            avg_r, max_m = services.calculate_statistics(movies)
            if not max_m:
                print("нет данных для статистики")
                continue
            print(f"\nсредний рейтинг всех фильмов: {avg_r}")
            print(f"фильм с максимальным рейтингом: {max_m}")
        elif choice == "7":
            if not movies:
                print("нечего экспортировать, добавьте фильмы!")
                continue
            export_to_csv(movies)
            print("данные успешно экспортированы в файл data.csv!")
        elif choice == "8":
            if not movies:
                print("список пуст, удалять нечего.")
                continue
            idx = get_num_input("введите номер фильма для удаления: ") - 1
            if 0 <= idx < len(movies):
                removed = movies.pop(idx)
                save_movies_to_json(movies)  # пересохраняем обновленный список
                print(f"фильм '{removed.name}' успешно удален!")
            else:
                print("неверный номер!")
        elif choice == "0":
            print("работа программы завершена")
            break
        else:
            print("неверный пункт меню, выберите от 0 до 8")


if __name__ == "__main__":
    main()