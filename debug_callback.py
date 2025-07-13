#!/usr/bin/env python3

# Тест логики обработки callback_data для криптоплатежей

def test_callback_logic():
    # Тестовые callback_data которые должны генерироваться
    test_cases = [
        "crypto_btc",           # Выбор Bitcoin -> должно показать меню сумм
        "crypto_btc_100",       # Выбор 100₽ для Bitcoin -> должно создать инвойс
        "crypto_btc_250",       # Выбор 250₽ для Bitcoin -> должно создать инвойс
        "crypto_btc_custom",    # Выбор своей суммы для Bitcoin -> должно запросить ввод
        "crypto_eth_500",       # Выбор 500₽ для Ethereum -> должно создать инвойс
        "crypto_usdt_1000",     # Выбор 1000₽ для USDT -> должно создать инвойс
        "crypto_ltc_2000",      # Выбор 2000₽ для Litecoin -> должно создать инвойс
    ]
    
    for data in test_cases:
        print(f"\nТестируем callback_data: {data}")
        print(f"startswith('crypto_'): {data.startswith('crypto_')}")
        
        # Проверка наличия криптовалют
        crypto_check = ("_btc" in data or "_eth" in data or "_usdt" in data or "_ltc" in data)
        print(f"Содержит криптовалюту: {crypto_check}")
        
        # Подсчет подчеркиваний
        underscore_count = data.count("_")
        print(f"Количество подчеркиваний: {underscore_count}")
        print(f"underscore_count >= 2: {underscore_count >= 2}")
        
        if data.startswith("crypto_") and crypto_check:
            if underscore_count >= 2:
                parts = data.split("_")
                print(f"Части: {parts}")
                if len(parts) >= 3:
                    crypto_type = parts[1]
                    amount = parts[2]
                    print(f"crypto_type: {crypto_type}, amount: {amount}")
                    if amount == "custom":
                        print("=> Должно вызвать handle_crypto_custom_amount")
                    else:
                        print("=> Должно вызвать handle_crypto_payment_amount")
                else:
                    print("=> Ошибка: недостаточно частей")
            else:
                crypto_type = data.split("_")[1]
                print(f"crypto_type: {crypto_type}")
                print("=> Должно вызвать handle_crypto_payment")
        
        print("-" * 50)

if __name__ == "__main__":
    test_callback_logic()