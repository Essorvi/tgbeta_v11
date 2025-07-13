#!/usr/bin/env python3

import asyncio
import sys
import os
import logging
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Симулируем окружение
os.environ['MONGO_URL'] = 'mongodb://localhost:27017'
os.environ['DB_NAME'] = 'telegram_bot_db'
os.environ['TELEGRAM_TOKEN'] = '7335902217:AAH0ocPm9dd48_qwvRkVVF6lGrj3K1s75us'
os.environ['CRYPTOBOT_TOKEN'] = '429820:AANv0kGVo4SahNRE0D3LOjFjL1eiUiSebql'
os.environ['CRYPTOBOT_BASE_URL'] = 'https://pay.crypt.bot/api'

async def test_callback_logic():
    """Прямой тест логики callback обработки"""
    
    # Тестовые данные
    callback_data_tests = [
        "crypto_btc",           # Должен показать меню сумм
        "crypto_btc_100",       # Должен создать инвойс на 100₽
        "crypto_btc_250",       # Должен создать инвойс на 250₽
        "crypto_btc_custom",    # Должен запросить ввод суммы
    ]
    
    for data in callback_data_tests:
        print(f"\n🧪 Тестируем callback_data: {data}")
        
        # Проверяем логику условий
        if data.startswith("crypto_"):
            print("✅ startswith('crypto_') - TRUE")
            
            if "_btc" in data or "_eth" in data or "_usdt" in data or "_ltc" in data:
                print("✅ Содержит криптовалюту - TRUE")
                
                underscore_count = data.count("_")
                print(f"📊 Количество подчеркиваний: {underscore_count}")
                
                if data.count("_") >= 2:
                    print("✅ data.count('_') >= 2 - TRUE")
                    parts = data.split("_")
                    print(f"📝 Части: {parts}")
                    
                    if len(parts) >= 3:
                        crypto_type = parts[1]
                        amount = parts[2]
                        print(f"💰 crypto_type: {crypto_type}, amount: {amount}")
                        
                        if amount == "custom":
                            print("🔧 Должен вызвать handle_crypto_custom_amount")
                        else:
                            print("💳 Должен вызвать handle_crypto_payment_amount")
                    else:
                        print("❌ Недостаточно частей в callback_data")
                else:
                    print("✅ data.count('_') < 2 - TRUE")
                    if len(data.split("_")) >= 2:
                        crypto_type = data.split("_")[1]
                        print(f"🏠 Должен вызвать handle_crypto_payment для {crypto_type}")
                    else:
                        print("❌ Не удалось извлечь crypto_type")
            else:
                print("❌ Не содержит известную криптовалюту")
        else:
            print("❌ Не начинается с 'crypto_'")
        
        print("-" * 60)

if __name__ == "__main__":
    print("🚀 Запуск прямого теста логики callback обработки...")
    asyncio.run(test_callback_logic())