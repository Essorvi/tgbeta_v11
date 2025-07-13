#!/usr/bin/env python3

import asyncio
import sys
import os
import logging

# Добавляем путь к backend для импорта модулей
sys.path.insert(0, '/app/backend')

# Импортируем необходимые функции из server.py
from server import handle_callback_query

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_crypto_callback():
    """Тест обработки crypto callback'ов"""
    
    # Симулируем callback query для нажатия на Bitcoin 100₽
    test_callback_query = {
        'id': 'test_callback_123',
        'from': {
            'id': 123456789,
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        },
        'message': {
            'chat': {'id': 123456789}
        },
        'data': 'crypto_btc_100'  # Это должно вызвать handle_crypto_payment_amount
    }
    
    print("🧪 Тестируем callback: crypto_btc_100")
    print("📝 Ожидается: вызов handle_crypto_payment_amount")
    print("-" * 50)
    
    try:
        await handle_callback_query(test_callback_query)
        print("✅ Callback обработан без ошибок")
    except Exception as e:
        print(f"❌ Ошибка при обработке callback: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Запуск теста crypto callback обработки...")
    asyncio.run(test_crypto_callback())