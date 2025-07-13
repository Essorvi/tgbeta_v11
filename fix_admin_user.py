#!/usr/bin/env python3
"""
Скрипт для исправления регистра username и установки админ статуса
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

async def fix_admin_user():
    """Исправляет регистр username и устанавливает админ статус"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Ищем пользователя с ID 1557902375 (реальный EriS)
        real_user_id = 1557902375
        user = await db.users.find_one({"telegram_id": real_user_id})
        
        if user:
            print(f"👤 Найден реальный пользователь:")
            print(f"  🆔 ID: {user.get('telegram_id')}")
            print(f"  👤 Имя: {user.get('first_name')}")
            print(f"  🔗 Username (до): '{user.get('username')}'")
            print(f"  👑 Админ (до): {user.get('is_admin')}")
            
            # Обновляем username на правильный и статус админа
            result = await db.users.update_one(
                {"telegram_id": real_user_id},
                {
                    "$set": {
                        "username": ADMIN_USERNAME,  # "eriksson_sop"
                        "is_admin": True
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"\n✅ Пользователь обновлен!")
                print(f"  🔗 Username (после): '{ADMIN_USERNAME}'")
                print(f"  👑 Админ (после): True")
                
                # Проверяем результат
                updated_user = await db.users.find_one({"telegram_id": real_user_id})
                print(f"\n🔍 Проверка обновления:")
                print(f"  🔗 Username: '{updated_user.get('username')}'")
                print(f"  👑 Админ: {updated_user.get('is_admin')}")
                print(f"  ✅ Совпадение: {updated_user.get('username') == ADMIN_USERNAME}")
            else:
                print("❌ Не удалось обновить пользователя")
                
        else:
            print(f"❌ Пользователь с ID {real_user_id} не найден")
            
        # Удаляем тестового пользователя чтобы избежать путаницы
        test_user_id = 123456789
        delete_result = await db.users.delete_one({"telegram_id": test_user_id})
        if delete_result.deleted_count > 0:
            print(f"\n🗑️ Удален тестовый пользователь (ID: {test_user_id})")
            
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(fix_admin_user())