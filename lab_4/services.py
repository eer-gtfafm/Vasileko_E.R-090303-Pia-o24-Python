def search_by_genre(movies, search_genre):
    """Поиск фильмов по жанру"""
    return [m for m in movies if m.genre.lower() == search_genre.lower()]


def filter_by_rating(movies, min_rating):
    """Фильтрация по минимальному рейтингу"""
    return [m for m in movies if m.rating >= min_rating]


def sort_movies_by_rating(movies):
    """Сортировка по убыванию рейтинга"""
    return sorted(movies, key=lambda x: x.rating, reverse=True)


def calculate_statistics(movies):
    """Расчет статистики"""
    if not movies:
        return 0, 0
    all_ratings = [m.rating for m in movies]
    avg_rating = round(sum(all_ratings) / len(movies), 2)
    max_movie = max(movies, key=lambda x: x.rating)
    return avg_rating, max_movie
