def add_movie(movies):
    print("\nдобавление нового фильма:")
    name_i = input('введите название фильма: ').strip()
    genre_i = input('введите жанр фильма: ').strip()
    while True:
        try:
            year_i = int(input('введите год выпуска: '))
            if year_i < 1895 or year_i > 2026:
                print('в этом году нет фильмов :(\nпопробуйте ввести другой год:')
                continue
            break
        except ValueError:
            print('введите год целым числом')
    while True:
        try:
            rating_i = float(input('введите рейтинг: '))
            if rating_i > 10 or rating_i < 0:
                print('рейтинг должен быть от 0 до 10')
                continue
            break
        except ValueError:
            print('введите число (можно дробное через точку), а не текст')
    movie_dict = {
        'name': name_i,
        'genre': genre_i,
        'year': year_i,
        'rating': rating_i
    }
    movies.append(movie_dict)
    print(f"фильм '{name_i}' успешно добавлен!")


def show_movies(movies):
    if not movies:
        print("\nсписок фильмов пока пуст :(")
        return
    print("\nсписок всех фильмов:")
    for idx, movie in enumerate(movies, 1):
        print(f"{idx}. {movie['name']} | Жанр: {movie['genre']} | Год: {movie['year']} | Рейтинг: {movie['rating']}")


def search_by_genre(movies, search_genre):
    return [m for m in movies if m['genre'].lower() == search_genre.lower()]


def filter_by_rating(movies, min_rating):
    return [m for m in movies if m['rating'] >= min_rating]


def sort_movies_by_rating(movies):
    return sorted(movies, key=lambda x: x['rating'], reverse=True)


def show_statistics(movies):
    if not movies:
        print("\nнет данных для расчета статистики")
        return
    total = len(movies)
    all_ratings = [m['rating'] for m in movies]
    avg_rating = round(sum(all_ratings) / total, 2)
    max_movie = max(movies, key=lambda x: x['rating'])
    
    print("\nстатистические показатели:")
    print(f"1) общее количество фильмов: {total}")
    print(f"2) средний рейтинг фильмов: {avg_rating}")
    print(f"3) фильм с максимальным рейтингом: '{max_movie['name']}' ({max_movie['rating']})")


def show_unique_genres(movies):
    if not movies:
        print("\nсписок фильмов пуст")
        return
    genres_set = set([m['genre'].strip().capitalize() for m in movies])
    print("\nмножество уникальных жанров:")
    for genre in genres_set:
        print(f"- {genre}")


def main():
    movies = []  
    while True: 
        print("\n===== МЕНЮ =====")
        print("1. добавить фильм")
        print("2. показать все фильмы")
        print("3. найти фильмы по жанру")
        print("4. фильтрация по рейтингу")
        print("5. сортировка по рейтингу")
        print("6. показать статистику")
        print("7. показать уникальные жанры")
        print("0. выход")
        choice = input("выберите действие: ").strip()
        if choice == "1":
            add_movie(movies)
        elif choice == "2":
            show_movies(movies)
        elif choice == "3":
            g = input("введите жанр для поиска: ").strip()
            found = search_by_genre(movies, g)
            if found:
                print(f"\nнайденные фильмы в жанре '{g}':")
                for m in found:
                    print(f"- {m['name']} ({m['year']}) — рейтинг: {m['rating']}")
            else:
                print(f"\nфильмы в жанре '{g}' не найдены")
        elif choice == "4":
            try:
                r = float(input("показать фильмы с рейтингом не ниже: "))
                filtered = filter_by_rating(movies, r)
                if filtered:
                    print(f"\nфильмы с рейтингом >= {r}:")
                    for m in filtered:
                        print(f"- {m['name']} рейтинг: {m['rating']} жанр: {m['genre']}")
                else:
                    print(f"\nфильмы с рейтингом {r} и выше отсутствуют")
            except ValueError:
                print("ошибка: рейтинг должен быть числом")
        elif choice == "5":
            sorted_list = sort_movies_by_rating(movies)
            print("\nфильмы, отсортированные по убыванию рейтинга")
            for m in sorted_list:
                print(f"[{m['rating']}] {m['name']} ({m['year']}) — {m['genre']}")
        elif choice == "6":
            show_statistics(movies)
        elif choice == "7":
            show_unique_genres(movies)
        elif choice == "0":
            print("работа программы завершена")
            break
        else:
            print("неверный пункт меню, выберите действие от 0 до 7")


if __name__ == '__main__':
    main()
