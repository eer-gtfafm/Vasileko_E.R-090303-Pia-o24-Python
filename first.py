def statistics(all_temp):  # считаем среднюю темп, макс, мин, положительную и жаркие дни
    sum_temp, count_more_0, hot_days = 0, 0, 0
    for temp in all_temp:  # для каждой введенной темп в списке
        sum_temp += temp  # общая сумма всех темп (для среднего)
        if temp > 0:
            count_more_0 += 1  # кол-во темп выше 0
        if temp > 25:  # 25 - порог
            hot_days += 1  # кол-во жарких дней
    average_temp = round(
        sum_temp / len(all_temp), 2
    )  # средняя темп, округленная до 2 знакоы после запятой
    max_temp = max(all_temp)
    min_temp = min(all_temp)
    return average_temp, max_temp, min_temp, count_more_0, hot_days  # возврат значений


def find_longest_pos_period(all_temp):  # находим самый длинный период теплых дней
    max_period = 0  # счетчик на макс период
    current_period = 0  # счетчик на текущий период
    for temp in all_temp:
        if temp > 0:
            current_period += 1  # +1 к продолжительности дней с темп выше 0
            if current_period > max_period:  # если больше макс, то перезаписываем
                max_period = current_period
        else:
            current_period = 0  # иначе прерываем период
    return max_period  # возвращаем макс


def main():  # основная функция
    days = int(input("введите количество дней наблюдения: "))
    if days <= 0:
        print("количество дней должно быть больше нуля.")
        return
    all_temp = []
    for i in range(days):
        temp = float(input(f"введите температуру для дня {i + 1}: "))  #
        all_temp.append(temp)
    avg_t, max_t, min_t, more_0, hot = statistics(all_temp)
    longest_pos_period = find_longest_pos_period(all_temp)
    print(f"средняя температура : {avg_t}°C")
    print(f"максимальная температура: {max_t}°C")
    print(f"минимальная температура: {min_t}°C")
    print(f"количество дней с температурой выше нуля: {more_0}")
    print(f"количество жарких дней (выше 25°C): {hot}")
    print(f"самый долгий период положительной температуры подряд: {longest_pos_period}")


if __name__ == "__main__":  # файл запущен напрямую, а не импортирован
    main()
