#!/usr/bin/env python3

import asyncio
import requests
import json
import sys
import os
from pathlib import Path

# Добавляем путь к backend
sys.path.insert(0, '/app/backend')

# Импортируем настройки
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')

# Импортируем функцию обработки
from server import handle_telegram_update

async def get_updates(offset=None):
    """Получить обновления от Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {
        "timeout": 10,
        "limit": 10
    }
    if offset:
        params["offset"] = offset
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Ошибка получения обновлений: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Исключение при получении обновлений: {e}")
        return None

async def poll_updates():
    """Polling обновлений от Telegram"""
    print("🤖 Запуск Telegram polling...")
    offset = None
    
    while True:
        try:
            result = await get_updates(offset)
            
            if result and result.get('ok'):
                updates = result.get('result', [])
                
                for update in updates:
                    update_id = update.get('update_id')
                    offset = update_id + 1
                    
                    print(f"📨 Получено обновление {update_id}")
                    
                    # Обрабатываем обновление
                    try:
                        await handle_telegram_update(update)
                        print(f"✅ Обновление {update_id} обработано")
                    except Exception as e:
                        print(f"❌ Ошибка обработки обновления {update_id}: {e}")
            
            await asyncio.sleep(1)  # Небольшая пауза между запросами
            
        except KeyboardInterrupt:
            print("🛑 Остановка polling...")
            break
        except Exception as e:
            print(f"❌ Ошибка в polling: {e}")
            await asyncio.sleep(5)  # Пауза при ошибке

if __name__ == "__main__":
    print(f"🔑 Token: {TELEGRAM_TOKEN[:10]}..." if TELEGRAM_TOKEN else "❌ Token не найден")
    asyncio.run(poll_updates())