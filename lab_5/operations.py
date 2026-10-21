def filter_movies(movie_list, predicate_func): # функция высшего порядка для фильтрации
    return filter(predicate_func, movie_list) # отбирает фильмы по переданной функции-условию


def transform_movies(movie_list, transform_func): # функция высшего порядка для преобразования
    return map(transform_func, movie_list) # превращает объекты фильмов в новые данные (например, имена)


def sort_movies(movie_list, key_func): # функция высшего порядка для сортировки 
    return sorted(movie_list, key=key_func) # сортирует список по правилу из переданной функции
