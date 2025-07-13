#!/usr/bin/env python3
"""
Скрипт для поиска реального пользователя eriksson_sop
"""

import asyncio
import os
import sys
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Загружаем переменные окружения
ROOT_DIR = Path(__file__).parent / 'backend'
load_dotenv(ROOT_DIR / '.env')

MONGO_URL = os.environ['MONGO_URL']
DB_NAME = os.environ['DB_NAME']
ADMIN_USERNAME = os.environ['ADMIN_USERNAME']

async def find_real_user():
    """Ищет реального пользователя eriksson_sop"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print(f"🔍 Ищем пользователя с username: '{ADMIN_USERNAME}'")
        print(f"📋 ADMIN_USERNAME из .env: '{ADMIN_USERNAME}'")
        print()
        
        # Ищем всех пользователей с похожим username
        users_cursor = db.users.find({
            "$or": [
                {"username": {"$regex": "eriksson", "$options": "i"}},
                {"username": ADMIN_USERNAME},
                {"username": f"@{ADMIN_USERNAME}"}
            ]
        })
        users = await users_cursor.to_list(length=None)
        
        print(f"👥 Найдено пользователей: {len(users)}")
        
        for user in users:
            print(f"\n👤 Пользователь:")
            print(f"  🆔 ID: {user.get('telegram_id')}")
            print(f"  👤 Имя: {user.get('first_name', 'N/A')}")
            print(f"  🔗 Username: '{user.get('username', 'N/A')}'")
            print(f"  👑 Админ: {user.get('is_admin', False)}")
            print(f"  📅 Создан: {user.get('created_at', 'N/A')}")
            print(f"  ⏰ Активен: {user.get('last_active', 'N/A')}")
            
            # Проверяем точное сравнение
            username = user.get('username', '')
            is_match = username == ADMIN_USERNAME
            print(f"  ✅ Точное совпадение с '{ADMIN_USERNAME}': {is_match}")
            
        # Показываем всех пользователей в системе
        all_users = await db.users.find({}).to_list(length=None)
        print(f"\n📊 Всего пользователей в системе: {len(all_users)}")
        
        print(f"\n📋 Последние 5 пользователей:")
        for user in all_users[-5:]:
            print(f"  - {user.get('first_name', 'N/A')} (@{user.get('username', 'N/A')}) [Admin: {user.get('is_admin', False)}]")
            
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(find_real_user())