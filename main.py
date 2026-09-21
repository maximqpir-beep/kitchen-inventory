from datetime import date


def get_usage_status(condition):
    if condition == "исправен":
        return "Разрешен к использованию"
    elif condition == "требует ремонта":
        return "Использование запрещено: требуется ремонт"
    elif condition == "списан":
        return "Использование запрещено: предмет списан"
    return "Использование запрещено: неизвестное состояние"


def calculate_total(quantity, unit_price):
    return quantity * unit_price


def can_move(condition, current_room, target_room):
    return (
        condition == "исправен"
        and bool(target_room.strip())
        and current_room.strip().casefold() != target_room.strip().casefold()
    )


def process_item():
    print("\nВыберите предмет:")
    print("1 — Кастрюля 5 л (1250.50 руб./шт.)")
    print("2 — Нож поварской (850.00 руб./шт.)")
    print("3 — Сковорода (1800.00 руб./шт.)")
    print("4 — Доска разделочная (450.00 руб./шт.)")
    print("5 — Половник (320.00 руб./шт.)")
    print("6 — Венчик (280.00 руб./шт.)")
    print("7 — Дуршлаг (650.00 руб./шт.)")
    print("8 — Противень (950.00 руб./шт.)")
    print("0 — Выход")

    item_choice = input("Номер предмета: ").strip()

    if item_choice == "0":
        return False
    elif item_choice == "1":
        item_name = "Кастрюля 5 л"
        category = "Посуда для приготовления"
        unit_price = 125050
    elif item_choice == "2":
        item_name = "Нож поварской"
        category = "Режущий инвентарь"
        unit_price = 85000
    elif item_choice == "3":
        item_name = "Сковорода"
        category = "Посуда для приготовления"
        unit_price = 180000
    elif item_choice == "4":
        item_name = "Доска разделочная"
        category = "Инвентарь для подготовки"
        unit_price = 45000
    elif item_choice == "5":
        item_name = "Половник"
        category = "Раздаточный инвентарь"
        unit_price = 32000
    elif item_choice == "6":
        item_name = "Венчик"
        category = "Инвентарь для подготовки"
        unit_price = 28000
    elif item_choice == "7":
        item_name = "Дуршлаг"
        category = "Инвентарь для подготовки"
        unit_price = 65000
    elif item_choice == "8":
        item_name = "Противень"
        category = "Посуда для выпечки"
        unit_price = 95000
    else:
        print("Ошибка: выберите номер от 0 до 8.")
        return True

    room = "Горячий цех"
    print(f"\nВыбрано: {item_name}")
    print(f"Текущее помещение: {room}")

    while True:
        quantity_text = input("Количество предметов (1–10000): ").strip()
        if (
            quantity_text.isascii()
            and quantity_text.isdecimal()
            and len(quantity_text) <= 5
        ):
            quantity = int(quantity_text)
            if 1 <= quantity <= 10000:
                break
        print("Ошибка: введите целое число от 1 до 10000.")

    print("\nСостояние:")
    print("1 — Исправен")
    print("2 — Требует ремонта")
    print("3 — Списан")

    while True:
        condition_choice = input("Номер состояния (1–3): ").strip()
        if condition_choice == "1":
            condition = "исправен"
            break
        elif condition_choice == "2":
            condition = "требует ремонта"
            break
        elif condition_choice == "3":
            condition = "списан"
            break
        print("Ошибка: выберите номер от 1 до 3.")

    print("\nПомещение назначения:")
    print("1 — Горячий цех")
    print("2 — Холодный цех")
    print("3 — Склад")
    print("4 — Моечная")

    while True:
        room_choice = input("Номер помещения (1–4): ").strip()
        if room_choice == "1":
            target_room = "Горячий цех"
            break
        elif room_choice == "2":
            target_room = "Холодный цех"
            break
        elif room_choice == "3":
            target_room = "Склад"
            break
        elif room_choice == "4":
            target_room = "Моечная"
            break
        print("Ошибка: выберите номер от 1 до 4.")

    total = calculate_total(quantity, unit_price)

    print(f"\nДата учета: {date.today():%d.%m.%Y}")
    print(f"Предмет: {item_name}; категория: {category}")
    print(f"Состояние: {condition}; количество: {quantity}")
    print(f"Стоимость партии: {total // 100}.{total % 100:02d} руб.")
    print(get_usage_status(condition))

    if can_move(condition, room, target_room):
        old_room = room
        room = target_room
        print(f"Перемещение выполнено: {old_room} -> {room}")
    elif room == target_room:
        print("Перемещение отклонено: предмет уже в этом помещении.")
    else:
        print("Перемещение отклонено: предмет должен быть исправен.")

    print(f"Текущее помещение: {room}")

    input("\nНажмите Enter, чтобы вернуться к выбору следующего предмета...")
    return True


def main():
    print("Система учета кухонного инвентаря | ЭФБО-12-24")
    print("Каждый выбор — новая партия. Данные партий не сохраняются.")

    while process_item():
        pass

    print("Программа завершена.")


if __name__ == "__main__":
    main()