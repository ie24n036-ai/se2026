import sys
from datetime import datetime

# --- 商品データ（マスター） ---
PRODUCTS = [
    {"id": 1, "name": "リンゴ", "price": 150},
    {"id": 2, "name": "バナナ", "price": 100},
    {"id": 3, "name": "オレンジ", "price": 120},
]

# これまでのすべての注文を足した合計金額
TOTAL_AMOUNT = 0

# 注文履歴
ORDER_HISTORY = []


def show_products():
    """商品一覧画面"""
    print("\n--- 商品一覧 ---")
    for p in PRODUCTS:
        print(f"ID: {p['id']} | {p['name']} - {p['price']}円")
    print("----------------")


def create_order():
    """注文入力・確認画面"""
    global TOTAL_AMOUNT

    cart = []

    while True:
        show_products()
        print(f"現在のカートの中身: {len(cart)}種類の商品が入っています")

        product_id_input = input(
            "購入したい商品のIDを入力してください (注文を終了して合計へ進む場合は 'q'): "
        )

        if product_id_input.lower() == "q":
            if not cart:
                print("カートが空なのでメニューに戻ります。")
                return
            break

        if not product_id_input.isdigit():
            print("【エラー】数字または 'q' を入力してください。")
            continue

        product_id = int(product_id_input)

        product = None
        for p in PRODUCTS:
            if p["id"] == product_id:
                product = p
                break

        if product is None:
            print("【エラー】その商品IDは見つかりません。")
            continue

        quantity_input = input(f"「{product['name']}」の数量を入力してください: ")

        if not quantity_input.isdigit():
            print("【エラー】正しい数量（数字）を入力してください。")
            continue

        quantity = int(quantity_input)

        if quantity <= 0:
            print("【エラー】数量は1以上にしてください。")
            continue

        cart.append(
            {
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity,
                "subtotal": product["price"] * quantity,
            }
        )

        print(f"🛒 カートに「{product['name']} × {quantity}個」を追加しました！")

        # さらに追加するか確認
        while True:
            next_choice = input("さらに商品を追加しますか？ (y/n): ").lower()

            if next_choice == "y":
                break

            elif next_choice == "n":
                break

            else:
                print("【エラー】y または n を入力してください。")

        if next_choice == "n":
            break

    # 注文確認画面
    print("\n=== 📄 今回の注文内容の確認 ===")

    current_total = 0
    items_summary = []

    for item in cart:
        summary_str = f"{item['name']} × {item['quantity']}個"
        print(f"・{summary_str} : {item['subtotal']}円")

        current_total += item["subtotal"]
        items_summary.append(summary_str)

    print("----------------------------")
    print(f"今回の小計: {current_total}円")
    print("==============================")

    # 注文確定確認
    while True:
        confirm = input("この注文を確定してよろしいですか？ (y/n): ").lower()

        if confirm == "y":
            TOTAL_AMOUNT += current_total

            order_time = datetime.now().strftime("%H:%M:%S")

            ORDER_HISTORY.append(
                {
                    "time": order_time,
                    "details": ", ".join(items_summary),
                    "total": current_total,
                }
            )

            print("✅ 注文を確定しました！")
            break

        elif confirm == "n":
            print("❌ 注文をキャンセルしました。")
            break

        else:
            print("【エラー】y または n を入力してください。")

    input("\n[Enter]キーを押すとメニューに戻ります...")


def show_history():
    """注文履歴画面"""
    print("\n=== 📜 注文履歴一覧 ===")

    if not ORDER_HISTORY:
        print("まだ確定された注文はありません。")
    else:
        for i, order in enumerate(ORDER_HISTORY, 1):
            print(
                f"[{i}] 時間: {order['time']} | 内容: {order['details']} | 金額: {order['total']}円"
            )

    print("==============================")
    print(f"💰 現在の合計金額: {TOTAL_AMOUNT}円")
    print("==============================")

    input("\n[Enter]キーを押すとメニューに戻ります...")


def show_total_only():
    """合計金額だけを表示"""
    print("\n==============================")
    print(f"💰 現在の合計金額: {TOTAL_AMOUNT}円")
    print("==============================")

    input("\n[Enter]キーを押すとメニューに戻ります...")


def main():
    """メニュー画面"""
    while True:
        print("\n=== メニュー ===")
        print("1. 商品一覧を表示")
        print("2. 商品を注文する")
        print("3. 注文履歴を表示")
        print("4. 合計金額だけを表示")
        print("5. 終了")
        print("================")

        choice = input("番号を選んでください (1-5): ")

        if choice == "1":
            show_products()

        elif choice == "2":
            create_order()

        elif choice == "3":
            show_history()

        elif choice == "4":
            show_total_only()

        elif choice == "5":
            print(f"\n最終の合計金額は【 {TOTAL_AMOUNT}円 】でした！")
            print("アプリを終了します。ありがとうございました！")
            sys.exit()

        else:
            print("【エラー】1から5の数字を選んでください。")


if __name__ == "__main__":
    main()
