#!/usr/bin/env python3

import asyncio
import requests
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('/app/backend/.env')

# Настраиваем логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CRYPTOBOT_TOKEN = os.environ.get('CRYPTOBOT_TOKEN')
CRYPTOBOT_BASE_URL = os.environ.get('CRYPTOBOT_BASE_URL')

async def create_cryptobot_invoice(amount: float, user_id: int, currency: str = "RUB"):
    """Создание CryptoBot инвойса - копия функции из server.py"""
    try:
        url = f"{CRYPTOBOT_BASE_URL}/createInvoice"
        headers = {
            "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
            "Content-Type": "application/json"
        }
        
        payload = {
            "currency_type": "fiat",
            "fiat": currency,
            "amount": str(amount),
            "description": f"Пополнение баланса УЗРИ для пользователя {user_id} на {amount}₽",
            "paid_btn_name": "callback",
            "paid_btn_url": "https://t.me/search1_test_bot",
            "payload": f"crypto_payment_{user_id}_{amount}"
        }
        
        logging.info(f"🤖 Создаем CryptoBot инвойс для {amount} {currency}")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        logging.info(f"📋 Результат: {result}")
        return result
        
    except Exception as e:
        logging.error(f"CryptoBot API error: {e}")
        return {"ok": False, "error": {"message": str(e)}}

async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown", reply_markup: dict = None):
    """Отправка сообщения в Telegram - копия функции из server.py"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = reply_markup
    
    try:
        logging.info(f"📤 Отправляем сообщение в чат {chat_id}")
        response = requests.post(url, json=payload, timeout=10)
        success = response.status_code == 200
        logging.info(f"📨 Статус отправки: {success} (код: {response.status_code})")
        if not success:
            logging.error(f"Ошибка отправки: {response.text}")
        return success
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

def create_back_keyboard():
    """Создание клавиатуры "Назад" """
    return {
        "inline_keyboard": [
            [{"text": "◀️ Назад в меню", "callback_data": "back_to_menu"}]
        ]
    }

async def simulate_handle_crypto_payment_amount(chat_id: int, user_id: int, crypto_type: str, amount: str):
    """Симуляция handle_crypto_payment_amount"""
    logging.info(f"💳 simulate_handle_crypto_payment_amount: chat_id={chat_id}, crypto_type={crypto_type}, amount={amount}")
    
    crypto_names = {
        "btc": "Bitcoin (BTC)",
        "eth": "Ethereum (ETH)", 
        "usdt": "USDT",
        "ltc": "Litecoin (LTC)"
    }
    
    try:
        amount_float = float(amount)
        logging.info(f"💰 Конвертированная сумма: {amount_float}")
        
        if amount_float < 100:
            logging.warning(f"❌ Сумма слишком мала: {amount_float}")
            await send_telegram_message(
                chat_id,
                "❌ Минимальная сумма пополнения: 100 ₽",
                reply_markup=create_back_keyboard()
            )
            return
            
        # Create CryptoBot invoice
        invoice_result = await create_cryptobot_invoice(amount_float, user_id, currency="RUB")
        
        if invoice_result.get('ok'):
            invoice_data = invoice_result.get('result', {})
            invoice_url = invoice_data.get('bot_invoice_url')
            invoice_id = invoice_data.get('invoice_id')
            
            logging.info(f"✅ Инвойс создан: ID={invoice_id}, URL={invoice_url}")
            
            if invoice_url:
                wallet_text = f"💰 *ПОПОЛНЕНИЕ ЧЕРЕЗ {crypto_names.get(crypto_type, crypto_type.upper())}*\n\n"
                wallet_text += f"💎 Сумма: {amount_float} ₽\n"
                wallet_text += f"📋 ID платежа: {invoice_id}\n\n"
                wallet_text += f"⚡ *Зачисление:* 1-30 минут после оплаты\n"
                wallet_text += f"📞 *Поддержка:* @Sigicara\n\n"
                wallet_text += f"👆 *Нажмите кнопку ниже для оплаты*"
                
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "💳 Оплатить", "url": invoice_url}],
                        [{"text": "◀️ Назад", "callback_data": "menu_balance"}]
                    ]
                }
                
                logging.info("📤 Отправляем сообщение с кнопкой оплаты")
                success = await send_telegram_message(chat_id, wallet_text, reply_markup=keyboard)
                if success:
                    logging.info("✅ Сообщение с инвойсом отправлено успешно")
                else:
                    logging.error("❌ Не удалось отправить сообщение с инвойсом")
            else:
                logging.error("❌ Нет URL инвойса в ответе")
                await send_telegram_message(
                    chat_id,
                    "❌ Ошибка создания платежа. Попробуйте позже.",
                    reply_markup=create_back_keyboard()
                )
        else:
            error_msg = invoice_result.get('error', {}).get('message', 'Неизвестная ошибка')
            logging.error(f"❌ Ошибка создания инвойса: {error_msg}")
            await send_telegram_message(
                chat_id,
                f"❌ Ошибка создания платежа: {error_msg}",
                reply_markup=create_back_keyboard()
            )
        
    except ValueError as e:
        logging.error(f"❌ Ошибка конвертации суммы: {e}")
        await send_telegram_message(
            chat_id,
            "❌ Неверная сумма",
            reply_markup=create_back_keyboard()
        )
    except Exception as e:
        logging.error(f"❌ Непредвиденная ошибка: {e}")
        await send_telegram_message(
            chat_id,
            "❌ Произошла ошибка. Попробуйте позже.",
            reply_markup=create_back_keyboard()
        )

async def test_full_crypto_flow():
    """Полный тест crypto flow"""
    print("🧪 Тестируем полный crypto flow...")
    
    # Тестовые данные
    test_chat_id = 123456789
    test_user_id = 123456789
    test_crypto_type = "btc"
    test_amount = "100"
    
    print(f"📝 Параметры теста:")
    print(f"   chat_id: {test_chat_id}")
    print(f"   user_id: {test_user_id}")
    print(f"   crypto_type: {test_crypto_type}")
    print(f"   amount: {test_amount}")
    print("-" * 50)
    
    try:
        await simulate_handle_crypto_payment_amount(test_chat_id, test_user_id, test_crypto_type, test_amount)
        print("✅ Тест завершен успешно")
    except Exception as e:
        print(f"❌ Ошибка в тесте: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Запуск полного теста crypto flow...")
    print(f"TELEGRAM_TOKEN: {'✅ Установлен' if TELEGRAM_TOKEN else '❌ Не найден'}")
    print(f"CRYPTOBOT_TOKEN: {'✅ Установлен' if CRYPTOBOT_TOKEN else '❌ Не найден'}")
    print(f"CRYPTOBOT_BASE_URL: {CRYPTOBOT_BASE_URL}")
    print()
    
    asyncio.run(test_full_crypto_flow())