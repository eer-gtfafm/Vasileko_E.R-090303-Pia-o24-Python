from generators import MovieIterator, get_movies_by_year_generator
from models import Movie
import operations
import sys  # для оценки эффективности генераторов по памяти


def get_num_input(prompt, is_float=False): # функция безопасного ввода чисел
    while True:
        try:
            return float(input(prompt)) if is_float else int(input(prompt))
        except ValueError:
            print("ошибка. введите числовое значение!")


def main(): # cтартовый набор данных
    movies = [
        Movie("Интерстеллар", "Фантастика", 2014, 8.6, 169),
        Movie("Начало", "Фантастика", 2010, 8.6, 148),
        Movie("Зеленая миля", "Драма", 1999, 9.1, 189),
        Movie("Побег из Шоушенка", "Драма", 1994, 9.1, 142),
        Movie("Джентльмены", "Комедия", 2019, 8.5, 113),
    ]
    while True:
        print("\n===== МЕНЮ =====")
        print("1. показать все фильмы")
        print("2. отфильтровать по рейтингу")
        print("3. получить только названия фильмов")
        print("4. отсортировать по продолжительности")
        print("5. рассчитать среднюю продолжительность")
        print("6. проверить наличие жанра в базе")
        print("7. ленивый генератор года")
        print("8. тест эффективности памяти")
        print("0. выход")
        choice = input("выберите действие: ").strip()
        if choice == "1":
            print("\nсписок всех фильмов в базе:")
            iterator = MovieIterator(movies) # работа личного класса-итератора
            for m in iterator:
                print(f"- {m}")
        elif choice == "2":
            r_i = get_num_input("введите минимальный рейтинг: ", is_float=True)
            filtered = operations.filter_movies(
                movies, lambda x: x.rating >= r_i
            )
            result = list(filtered)
            if result:
                print(f"\nфильмы с рейтингом >= {r_i}:")
                for m in result:
                    print(f"- {m}")
            else:
                print("нет таких фильмов.")
        elif choice == "3":
            names_map = operations.transform_movies(movies, lambda x: x.name)
            names_list = [name for name in names_map]
            print("\nтолько названия всех фильмов в базе:")
            for name in names_list:
                print(f"- {name}")
        elif choice == "4":
            sorted_list = operations.sort_movies(movies, lambda x: x.duration)
            print("\nфильмы, отсортированные по возрастанию длительности:")
            for m in sorted_list:
                print(f"- {m.name} ({m.duration} мин.)")
        elif choice == "5":
            if not movies:
                continue
            durations = [m.duration for m in movies]  
            avg_duration = round(sum(durations) / len(movies), 2)
            print(f"\nсредняя продолжительность фильмов: {avg_duration} мин.")
        elif choice == "6":
            genre_i = input("какой жанр проверить?: ").strip().lower()
            has_genre = any(m.genre.lower() == genre_i for m in movies)
            if has_genre:
                print(f"да! в базе есть фильмы с жанром '{genre_i}'")
            else:
                print(f"нет, фильмов жанра '{genre_i}' в базе не обнаружено")
        elif choice == "7":
            year_i = get_num_input("фильмы какого года выдать?: ")
            print(f"\nзапуск генератора для {year_i} года:")
            gen = get_movies_by_year_generator(movies, year_i)
            found = False
            while True:
                try:
                    m = next(gen)
                    print(f"генератор выдал объект: {m}")
                    found = True
                except StopIteration:
                    print("генератор успешно завершил выдачу данных.")
                    break
            if not found:
                print("в этом году фильмов нет.")
        elif choice == "8":
            print("\n--- ДЕМОНСТРАЦИЯ ЛЕНИВЫХ ВЫЧИСЛЕНИЙ ---")
            limit = 1000000
            list_res = [x * x for x in range(limit)]
            gen_res = (x * x for x in range(limit))
            print(f"размер обычного списка в памяти: {sys.getsizeof(list_res)} байт")
            print(f"размер ленивого генератора в памяти: {sys.getsizeof(gen_res)} байт")
            print("вывод: генератор занимает в разы меньше памяти, так как считает на лету!")
        elif choice == "0":
            print("работа программы завершена.")
            break


if __name__ == "__main__":
    main()