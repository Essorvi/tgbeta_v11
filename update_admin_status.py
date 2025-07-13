#!/usr/bin/env python3
"""
Скрипт для обновления админ статуса пользователя @eriksson_sop
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

async def update_admin_status():
    """Обновляет админ статус для пользователя eriksson_sop"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Ищем пользователя с username eriksson_sop
        user = await db.users.find_one({"username": ADMIN_USERNAME})
        
        if user:
            print(f"👤 Найден пользователь: {user.get('first_name', 'N/A')} (@{user.get('username', 'N/A')})")
            print(f"🆔 Telegram ID: {user.get('telegram_id')}")
            print(f"👑 Текущий админ статус: {user.get('is_admin', False)}")
            
            # Обновляем статус админа
            result = await db.users.update_one(
                {"username": ADMIN_USERNAME},
                {"$set": {"is_admin": True}}
            )
            
            if result.modified_count > 0:
                print(f"✅ Админ статус успешно обновлен для @{ADMIN_USERNAME}")
            else:
                print(f"ℹ️  Админ статус уже был установлен для @{ADMIN_USERNAME}")
                
        else:
            print(f"❌ Пользователь @{ADMIN_USERNAME} не найден в базе данных")
            print("💡 Сначала отправьте /start боту, чтобы создать аккаунт")
            
        # Показываем всех админов в системе
        admins = await db.users.find({"is_admin": True}).to_list(length=None)
        print(f"\n👑 Админы в системе: {len(admins)}")
        for admin in admins:
            print(f"  - @{admin.get('username', 'N/A')} (ID: {admin.get('telegram_id')})")
            
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_admin_status())