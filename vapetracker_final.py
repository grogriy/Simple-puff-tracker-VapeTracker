import os
import json
import math
import datetime
import matplotlib.pyplot as plt

def get_data_file():
    """Возвращает имя файла для хранения данных."""
    return "vapetracker_data.json"

def get_today_str():
    """Возвращает сегодняшнюю дату в формате 'YYYY-MM-DD'."""
    return datetime.datetime.today().strftime('%Y-%m-%d')

def load_data():
    """
    Загружает данные из JSON-файла.
    Если файл не существует или содержит ошибку, возвращает базовую структуру с пустым словарём для 'puffs'.
    """
    filename = get_data_file()
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            data = {}
    else:
        data = {}
    # Обеспечиваем наличие ключа "puffs"
    if not isinstance(data, dict):
        data = {}
    if "puffs" not in data:
        data["puffs"] = {}
    return data

def save_data(data):
    """Сохраняет данные в JSON-файл с отступами для читаемости."""
    filename = get_data_file()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def add_puffs(date, count):
    """
    Добавляет указанное количество затяжек для заданной даты.

    Аргументы:
        date (str): дата в формате 'YYYY-MM-DD'
        count (int): количество затяжек
    """
    data = load_data()
    if "puffs" not in data:
        data["puffs"] = {}
    if date in data["puffs"]:
        data["puffs"][date] += count
    else:
        data["puffs"][date] = count
    save_data(data)

def show_progress():
    """
    Отображает график прогресса отказа от курения.
    Если установлена цель (план), на графике показаны две линии:
      - Допустимое количество затяжек по плану.
      - Фактическое количество затяжек.
    Если цели не установлено, строится график фактических затяжек по датам.
    """
    data = load_data()

    if "goal" in data:
        goal = data["goal"]
        try:
            start_date = datetime.datetime.strptime(goal["start_date"], '%Y-%m-%d')
        except (KeyError, ValueError):
            print("Ошибка в данных цели. Проверьте настройки плана.")
            return

        initial = goal.get("initial", 0)
        total_days = goal.get("total_days", 0)
        daily_reduction = goal.get("daily_reduction", 0)

        allowed_dates = []
        allowed_values = []
        # Формируем расписание допустимых значений от исходного количества до 0
        for i in range(total_days):
            day_date = start_date + datetime.timedelta(days=i)
            date_str = day_date.strftime('%Y-%m-%d')
            allowed_dates.append(date_str)
            allowed_val = max(round(initial - daily_reduction * i), 0)
            allowed_values.append(allowed_val)

        # Получаем фактические данные для каждого дня плана (если данных нет – 0)
        actual_values = [data["puffs"].get(d, 0) for d in allowed_dates]

        plt.figure(figsize=(10, 5))
        plt.plot(allowed_dates, allowed_values, marker="o", linestyle="--", label="Допустимое количество затяжек")
        plt.plot(allowed_dates, actual_values, marker="s", linestyle="-", label="Фактическое количество затяжек")
        plt.xlabel("Дата")
        plt.ylabel("Количество затяжек")
        plt.title("Прогресс отказа от курения")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    else:
        # Если цель не установлена, показываем только фактические данные
        puffs_data = load_data().get("puffs", {})
        if not puffs_data:
            print("Нет данных для отображения.")
            return
        dates = sorted(puffs_data.keys())
        counts = [puffs_data[d] for d in dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, counts, marker="o", linestyle="-", label="Фактическое количество затяжек")
        plt.xlabel("Дата")
        plt.ylabel("Количество затяжек")
        plt.title("Прогресс отказа от курения")
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def set_goal():
    """
    Функция установки цели отказа от курения.
    Пользователь задаёт исходное (среднее) количество затяжек за день и выбирает способ установки цели:
      1. Указать конкретное количество дней до полного отказа.
      2. Выбрать один из предложенных планов снижения (плавный, средний, быстрый).
         При выборе плана можно задать желаемое снижение в день и/или выбрать один из стандартных сроков.

    Сохраняются следующие данные:
      - start_date: дата установки плана (текущая дата)
      - initial: исходное количество затяжек
      - total_days: общее количество дней до полного отказа
      - daily_reduction: величина снижения затяжек за день
    """
    # Запрос исходного количества затяжек
    while True:
        try:
            initial = float(input("Введите ваше первоначальное среднее количество затяжек за день: "))
            if initial < 0:
                print("Количество затяжек не может быть отрицательным. Попробуйте снова.")
                continue
            break
        except ValueError:
            print("Ошибка ввода. Введите число.")

    # Выбор способа установки цели
    while True:
        print("\nВыберите способ установки цели отказа от курения:")
        print("1 - Указать количество дней до полного отказа.")
        print("2 - Выбрать один из предложенных планов снижения (плавный, средний, быстрый).")
        choice = input("Введите 1 или 2: ")

        if choice == "1":
            try:
                days = int(input("Введите количество дней до полного отказа: "))
                if days < 1:
                    print("Количество дней должно быть не менее 1. Попробуйте снова.")
                    continue
                daily_reduction = initial if days == 1 else initial / (days - 1)
                total_days = days
                break
            except ValueError:
                print("Ошибка ввода. Введите целое число.")
        elif choice == "2":
            print("\nВыберите план снижения:")
            print("1 - Плавный выход (снижение на 2–5 затяжек в день).")
            print("2 - Средний выход (снижение на 6–9 затяжек в день).")
            print("3 - Быстрый выход (снижение от 10 затяжек в день).")
            plan_choice = input("Введите 1, 2 или 3: ")

            if plan_choice == "1":
                default_reduction = 3
                allowed_range = (2, 5)
            elif plan_choice == "2":
                default_reduction = 7
                allowed_range = (6, 9)
            elif plan_choice == "3":
                default_reduction = 10
                allowed_range = (10, float('inf'))
            else:
                print("Неверный выбор. Попробуйте снова.")
                continue

            try:
                user_input = input(
                    f"Введите желаемое снижение затяжек в день (рекомендуется {default_reduction}, "
                    f"диапазон {allowed_range[0]}–{allowed_range[1] if allowed_range[1]!=float('inf') else 'и выше'}),\n"
                    "или нажмите Enter для использования значения по умолчанию: "
                )
                if user_input.strip() == "":
                    daily_reduction = default_reduction
                else:
                    daily_reduction = float(user_input)
                    if daily_reduction < allowed_range[0] or (allowed_range[1] != float('inf') and daily_reduction > allowed_range[1]):
                        print(f"Введённое значение должно быть в диапазоне {allowed_range[0]}–"
                              f"{allowed_range[1] if allowed_range[1]!=float('inf') else 'и выше'}. Попробуйте снова.")
                        continue
            except ValueError:
                print("Ошибка ввода. Попробуйте снова.")
                continue

            # Расчёт приблизительного количества дней до полного отказа
            total_days = math.ceil(initial / daily_reduction) + 1
            print(f"\nРассчитанное количество дней до полного отказа: {total_days} дней.")

# Предлагаем выбрать один из стандартных сроков
            print("\nВыберите один из предложенных сроков:")
            print("1 - Неделя (7 дней)")
            print("2 - Месяц (30 дней)")
            print("3 - Полтора месяца (45 дней)")
            print("4 - Три месяца (90 дней)")
            print("5 - Полгода (180 дней)")
            print("6 - Год (365 дней)")
            print("7 - Использовать рассчитанный срок")
            duration_choice = input("Введите номер выбранного варианта: ")
            durations = {
                "1": 7,
                "2": 30,
                "3": 45,
                "4": 90,
                "5": 180,
                "6": 365
            }
            if duration_choice in durations:
                chosen_days = durations[duration_choice]
                daily_reduction = initial if chosen_days == 1 else initial / (chosen_days - 1)
                total_days = chosen_days
                print(f"\nВыбран срок: {total_days} дней. Новое ежедневное снижение: {daily_reduction:.2f} затяжек в день.")
            else:
                print("Будет использован рассчитанный ранее срок.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

    # Устанавливаем дату начала плана (текущая дата)
    start_date = get_today_str()

    # Сохраняем цель (план) в файле данных
    data = load_data()
    data["goal"] = {
        "start_date": start_date,
        "initial": initial,
        "total_days": total_days,
        "daily_reduction": daily_reduction
    }
    save_data(data)
    print("\nЦель отказа от курения успешно установлена!")

def main():
    """
    Основная функция программы.
    Меню:
      1. Добавить затяжки за сегодня.
      2. Показать график прогресса.
      3. Установить цель отказа от курения.
      4. Выход.
    """
    while True:
        print("\nМеню:")
        print("1. Добавить затяжки")
        print("2. Показать прогресс")
        print("3. Установить цель отказа от курения")
        print("4. Выход")
        choice = input("Введите ваш выбор: ")

        if choice == "1":
            try:
                count = int(input("Введите количество затяжек: "))
                if count < 0:
                    raise ValueError("Количество не может быть отрицательным.")
                add_puffs(get_today_str(), count)
                print("Затяжки успешно добавлены!")
            except ValueError as e:
                print(f"Ошибка ввода: {e}")

        elif choice == "2":
            show_progress()

        elif choice == "3":
            set_goal()

        elif choice == "4":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()