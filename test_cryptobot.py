#!/usr/bin/env python3

import requests
import os
import asyncio
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('/app/backend/.env')

CRYPTOBOT_TOKEN = os.environ.get('CRYPTOBOT_TOKEN')
CRYPTOBOT_BASE_URL = os.environ.get('CRYPTOBOT_BASE_URL')

async def test_cryptobot_invoice():
    """Тест создания CryptoBot инвойса"""
    try:
        url = f"{CRYPTOBOT_BASE_URL}/createInvoice"
        headers = {
            "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
            "Content-Type": "application/json"
        }
        
        test_amount = 100.0
        test_user_id = 123456789
        
        payload = {
            "currency_type": "fiat",
            "fiat": "RUB",
            "amount": str(test_amount),
            "description": f"Пополнение баланса УЗРИ для пользователя {test_user_id} на {test_amount}₽",
            "paid_btn_name": "callback",
            "paid_btn_url": "https://t.me/search1_test_bot",
            "payload": f"crypto_payment_{test_user_id}_{test_amount}"
        }
        
        print("🤖 Тестируем создание CryptoBot инвойса...")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        print("-" * 50)
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print("✅ Инвойс создан успешно!")
                invoice_data = result.get('result', {})
                print(f"Invoice ID: {invoice_data.get('invoice_id')}")
                print(f"Invoice URL: {invoice_data.get('bot_invoice_url')}")
                return result
            else:
                print("❌ Ошибка при создании инвойса!")
                print(f"Error: {result}")
                return result
        else:
            print("❌ HTTP ошибка!")
            return {"ok": False, "error": {"message": f"HTTP {response.status_code}"}}
        
    except Exception as e:
        print(f"❌ Исключение: {e}")
        return {"ok": False, "error": {"message": str(e)}}

if __name__ == "__main__":
    print(f"CRYPTOBOT_TOKEN: {CRYPTOBOT_TOKEN[:10]}..." if CRYPTOBOT_TOKEN else "CRYPTOBOT_TOKEN not found")
    print(f"CRYPTOBOT_BASE_URL: {CRYPTOBOT_BASE_URL}")
    print()
    
    result = asyncio.run(test_cryptobot_invoice())