"""Отдельная программа «Холодильник», не часть учета инвентаря."""

from fridge import add, amount, expired, find


def main() -> None:
    goods = {}
    print("Холодильник. Количества вводятся в одной единице, например кг.")
    try:
        while True:
            print("\n1 — Добавить; 2 — Содержимое; 3 — Поиск")
            print("4 — Срок истекает сегодня или раньше; 0 — Выход")
            choice = input("Выбор: ").strip()
            try:
                if choice == "0":
                    return
                elif choice == "1":
                    title = input("Продукт: ")
                    quantity = input("Количество: ")
                    expiry = input("Срок ГГГГ-ММ-ДД (Enter — без срока): ")
                    add(goods, title, quantity, expiry.strip() or None)
                    print("Добавлено.")
                elif choice == "2":
                    if not goods:
                        print("Холодильник пуст.")
                    for title, batches in goods.items():
                        for batch in batches:
                            print(title, batch["amount"],
                                  batch["expiration_date"] or "без срока")
                elif choice == "3":
                    query = input("Часть названия: ")
                    print("Найдено:", find(goods, query))
                    print("Общее количество:", amount(goods, query))
                elif choice == "4":
                    print(expired(goods))
                else:
                    print("Выберите номер от 0 до 4.")
            except ValueError as error:
                print(error)
    except (EOFError, KeyboardInterrupt):
        print("\nВыход.")


if __name__ == "__main__":
    main()
