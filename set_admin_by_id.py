#!/usr/bin/env python3
"""
Скрипт для установки админ статуса по Telegram ID
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
ADMIN_TELEGRAM_ID = int(os.environ['ADMIN_TELEGRAM_ID'])

async def set_admin_by_id():
    """Устанавливает админ статус по Telegram ID"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        print(f"🔍 Устанавливаем админ статус для Telegram ID: {ADMIN_TELEGRAM_ID}")
        
        # Ищем пользователя по ID
        user = await db.users.find_one({"telegram_id": ADMIN_TELEGRAM_ID})
        
        if user:
            print(f"👤 Найден пользователь:")
            print(f"  🆔 ID: {user.get('telegram_id')}")
            print(f"  👤 Имя: {user.get('first_name')}")
            print(f"  🔗 Username: {user.get('username')}")
            print(f"  👑 Админ (до): {user.get('is_admin')}")
            
            # Устанавливаем админ статус
            result = await db.users.update_one(
                {"telegram_id": ADMIN_TELEGRAM_ID},
                {"$set": {"is_admin": True}}
            )
            
            if result.modified_count > 0:
                print(f"\n✅ Админ статус установлен для ID {ADMIN_TELEGRAM_ID}")
            else:
                print(f"\nℹ️  Админ статус уже был установлен для ID {ADMIN_TELEGRAM_ID}")
                
            # Проверяем результат
            updated_user = await db.users.find_one({"telegram_id": ADMIN_TELEGRAM_ID})
            print(f"  👑 Админ (после): {updated_user.get('is_admin')}")
            
        else:
            print(f"❌ Пользователь с ID {ADMIN_TELEGRAM_ID} не найден в базе данных")
            print("💡 Сначала отправьте /start боту, чтобы создать аккаунт")
            
        # Убираем админ статус у всех остальных пользователей для безопасности
        remove_result = await db.users.update_many(
            {"telegram_id": {"$ne": ADMIN_TELEGRAM_ID}},
            {"$set": {"is_admin": False}}
        )
        
        if remove_result.modified_count > 0:
            print(f"\n🔒 Убран админ статус у {remove_result.modified_count} других пользователей")
            
        # Показываем всех админов
        admins = await db.users.find({"is_admin": True}).to_list(length=None)
        print(f"\n👑 Админы в системе: {len(admins)}")
        for admin in admins:
            print(f"  - {admin.get('first_name')} (@{admin.get('username')}) [ID: {admin.get('telegram_id')}]")
            
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(set_admin_by_id())