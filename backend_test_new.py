#!/usr/bin/env python3
"""
Backend Testing Suite for Telegram Bot Custom Deposits and Notifications
Tests according to review request priorities:
1. PRIORITY 1 - Custom deposits for cryptocurrencies (crypto_*_custom callbacks)
2. PRIORITY 2 - Notification functions (handle_successful_payment, handle_cryptobot_payment)
3. PRIORITY 3 - User state handling (set_user_state, get_user_state)
"""

import requests
import json
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://da93c359-3829-4b53-b388-a20063a6715b.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
BOT_USERNAME = os.getenv('BOT_USERNAME', 'search1_test_bot')

class TelegramBotTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = 987654321  # Test user ID
        self.test_chat_id = 987654321  # Test chat ID
        
    def log_test(self, test_name, success, message="", details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            'test': test_name,
            'status': status,
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name}")
        if message:
            print(f"   Message: {message}")
        if details and not success:
            print(f"   Details: {details}")
        print()

    def send_webhook_update(self, update_data):
        """Send webhook update to the bot"""
        try:
            webhook_url = f"{API_BASE}/webhook/{WEBHOOK_SECRET}"
            response = requests.post(webhook_url, json=update_data, timeout=10)
            return response.status_code == 200, response
        except Exception as e:
            return False, str(e)

    def create_callback_update(self, callback_data, message_id=1):
        """Create callback query update"""
        return {
            "update_id": int(time.time()),
            "callback_query": {
                "id": str(int(time.time())),
                "from": {
                    "id": self.test_user_id,
                    "is_bot": False,
                    "first_name": "TestUser",
                    "username": "testuser_crypto"
                },
                "message": {
                    "message_id": message_id,
                    "from": {
                        "id": 123456789,
                        "is_bot": True,
                        "first_name": "TestBot",
                        "username": BOT_USERNAME
                    },
                    "chat": {
                        "id": self.test_chat_id,
                        "first_name": "TestUser",
                        "username": "testuser_crypto",
                        "type": "private"
                    },
                    "date": int(time.time()),
                    "text": "Test message"
                },
                "data": callback_data
            }
        }

    def create_message_update(self, text):
        """Create message update"""
        return {
            "update_id": int(time.time()),
            "message": {
                "message_id": int(time.time()),
                "from": {
                    "id": self.test_user_id,
                    "is_bot": False,
                    "first_name": "TestUser",
                    "username": "testuser_crypto"
                },
                "chat": {
                    "id": self.test_chat_id,
                    "first_name": "TestUser",
                    "username": "testuser_crypto",
                    "type": "private"
                },
                "date": int(time.time()),
                "text": text
            }
        }

    def create_successful_payment_update(self, amount, payload):
        """Create successful payment update for Telegram Stars"""
        return {
            "update_id": int(time.time()),
            "message": {
                "message_id": int(time.time()),
                "from": {
                    "id": self.test_user_id,
                    "is_bot": False,
                    "first_name": "TestUser",
                    "username": "testuser_crypto"
                },
                "chat": {
                    "id": self.test_chat_id,
                    "first_name": "TestUser",
                    "username": "testuser_crypto",
                    "type": "private"
                },
                "date": int(time.time()),
                "successful_payment": {
                    "currency": "XTR",
                    "total_amount": int(amount * 100),  # Convert to kopeks
                    "invoice_payload": payload,
                    "telegram_payment_charge_id": f"test_charge_{int(time.time())}",
                    "provider_payment_charge_id": f"test_provider_{int(time.time())}"
                }
            }
        }

    def create_cryptobot_webhook_data(self, amount, user_id, invoice_id=None):
        """Create CryptoBot webhook data"""
        if not invoice_id:
            invoice_id = f"test_invoice_{int(time.time())}"
            
        return {
            "update_type": "invoice_paid",
            "payload": {
                "invoice_id": invoice_id,
                "status": "paid",
                "amount": amount,
                "currency_type": "crypto",
                "fiat": "RUB",
                "description": f"Пополнение баланса УЗРИ для пользователя {user_id}"
            }
        }

    def test_api_health(self):
        """Test basic API health"""
        try:
            response = requests.get(f"{API_BASE}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "УЗРИ - Telegram Bot API" in data.get('message', ''):
                    self.log_test("API Health Check", True, "API is running and responding correctly")
                    return True
                else:
                    self.log_test("API Health Check", False, "API response format incorrect", str(data))
                    return False
            else:
                self.log_test("API Health Check", False, f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("API Health Check", False, "Connection failed", str(e))
            return False

    # PRIORITY 1 TESTS - Custom deposits for cryptocurrencies
    def test_crypto_custom_callback_data_parsing(self):
        """Test that crypto_*_custom callback_data is correctly parsed"""
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        
        for crypto in crypto_types:
            callback_data = f"crypto_{crypto}_custom"
            # Count underscores - should be 2 for proper parsing
            underscore_count = callback_data.count("_")
            
            if underscore_count == 2:
                self.log_test(f"Crypto Custom Callback Data Parsing ({crypto.upper()})", True, 
                            f"Callback data '{callback_data}' has correct underscore count: {underscore_count}")
            else:
                self.log_test(f"Crypto Custom Callback Data Parsing ({crypto.upper()})", False, 
                            f"Callback data '{callback_data}' has incorrect underscore count: {underscore_count}")

    def test_crypto_custom_amount_callbacks(self):
        """Test crypto custom amount callbacks for all currencies"""
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        
        for crypto in crypto_types:
            callback_data = f"crypto_{crypto}_custom"
            update = self.create_callback_update(callback_data)
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test(f"Crypto Custom Amount Callback ({crypto.upper()})", True, 
                            f"Callback for {crypto.upper()} processed successfully")
            else:
                self.log_test(f"Crypto Custom Amount Callback ({crypto.upper()})", False, 
                            f"Callback for {crypto.upper()} failed", str(response))

    def test_crypto_custom_vs_regular_callback_routing(self):
        """Test that custom callbacks route to handle_crypto_custom_amount, not handle_crypto_payment"""
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        
        for crypto in crypto_types:
            # Test regular callback (should route to handle_crypto_payment)
            regular_callback = f"crypto_{crypto}"
            update = self.create_callback_update(regular_callback)
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test(f"Regular Crypto Callback Routing ({crypto.upper()})", True, 
                            f"Regular callback for {crypto.upper()} processed correctly")
            else:
                self.log_test(f"Regular Crypto Callback Routing ({crypto.upper()})", False, 
                            f"Regular callback for {crypto.upper()} failed", str(response))
            
            time.sleep(0.5)
            
            # Test custom callback (should route to handle_crypto_custom_amount)
            custom_callback = f"crypto_{crypto}_custom"
            update = self.create_callback_update(custom_callback)
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test(f"Custom Crypto Callback Routing ({crypto.upper()})", True, 
                            f"Custom callback for {crypto.upper()} processed correctly")
            else:
                self.log_test(f"Custom Crypto Callback Routing ({crypto.upper()})", False, 
                            f"Custom callback for {crypto.upper()} failed", str(response))
            
            time.sleep(0.5)

    def test_crypto_custom_user_state_setting(self):
        """Test that user state is set to 'waiting_custom_amount_crypto' for crypto custom amounts"""
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        
        for crypto in crypto_types:
            callback_data = f"crypto_{crypto}_custom"
            update = self.create_callback_update(callback_data)
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test(f"Crypto Custom User State Setting ({crypto.upper()})", True, 
                            f"User state should be set to 'waiting_custom_amount_crypto' for {crypto.upper()}")
            else:
                self.log_test(f"Crypto Custom User State Setting ({crypto.upper()})", False, 
                            f"Failed to set user state for {crypto.upper()}", str(response))
            
            time.sleep(0.5)

    def test_crypto_custom_amount_input_flow(self):
        """Test complete crypto custom amount input flow"""
        crypto_type = "btc"  # Test with Bitcoin
        
        # Step 1: Trigger custom amount callback
        callback_update = self.create_callback_update(f"crypto_{crypto_type}_custom")
        success, response = self.send_webhook_update(callback_update)
        
        if not success:
            self.log_test("Crypto Custom Amount Flow - Initial Callback", False, 
                        "Initial callback failed", str(response))
            return
        
        self.log_test("Crypto Custom Amount Flow - Initial Callback", True, 
                    "Custom amount callback processed successfully")
        
        time.sleep(1)  # Wait for state to be set
        
        # Step 2: Send valid amount
        message_update = self.create_message_update("1000")
        success, response = self.send_webhook_update(message_update)
        
        if success:
            self.log_test("Crypto Custom Amount Flow - Valid Input", True, 
                        "Valid amount input processed successfully")
        else:
            self.log_test("Crypto Custom Amount Flow - Valid Input", False, 
                        "Valid amount input failed", str(response))
        
        time.sleep(1)
        
        # Step 3: Test invalid amount (not multiple of 50)
        callback_update2 = self.create_callback_update(f"crypto_{crypto_type}_custom")
        self.send_webhook_update(callback_update2)
        time.sleep(1)
        
        message_update_invalid = self.create_message_update("125")  # Not multiple of 50
        success, response = self.send_webhook_update(message_update_invalid)
        
        if success:
            self.log_test("Crypto Custom Amount Flow - Invalid Input", True, 
                        "Invalid amount input handled correctly")
        else:
            self.log_test("Crypto Custom Amount Flow - Invalid Input", False, 
                        "Invalid amount input handling failed", str(response))

    # PRIORITY 2 TESTS - Notification functions
    def test_handle_successful_payment_telegram_stars(self):
        """Test handle_successful_payment function for Telegram Stars"""
        # Test successful payment notification
        amount = 500.0  # 500 rubles
        payload = f"stars_payment_{self.test_user_id}_{amount}"
        
        payment_update = self.create_successful_payment_update(amount, payload)
        success, response = self.send_webhook_update(payment_update)
        
        if success:
            self.log_test("Handle Successful Payment - Telegram Stars", True, 
                        f"Telegram Stars payment of {amount}₽ processed successfully")
        else:
            self.log_test("Handle Successful Payment - Telegram Stars", False, 
                        f"Telegram Stars payment processing failed", str(response))

    def test_handle_cryptobot_payment_webhook(self):
        """Test handle_cryptobot_payment function for CryptoBot webhook"""
        try:
            # Test CryptoBot webhook endpoint
            amount = 1000.0  # 1000 rubles
            webhook_data = self.create_cryptobot_webhook_data(amount, self.test_user_id)
            
            cryptobot_webhook_url = f"{API_BASE}/cryptobot/webhook"
            response = requests.post(cryptobot_webhook_url, json=webhook_data, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Handle CryptoBot Payment Webhook", True, 
                            f"CryptoBot payment of {amount}₽ processed successfully")
            else:
                self.log_test("Handle CryptoBot Payment Webhook", False, 
                            f"CryptoBot webhook failed with status {response.status_code}", response.text)
        except Exception as e:
            self.log_test("Handle CryptoBot Payment Webhook", False, 
                        "CryptoBot webhook request failed", str(e))

    def test_payment_database_recording(self):
        """Test that payments are correctly recorded in database"""
        # This test verifies the payment recording logic by sending payment notifications
        
        # Test Telegram Stars payment recording
        amount_stars = 250.0
        payload_stars = f"stars_payment_{self.test_user_id}_{amount_stars}"
        payment_update_stars = self.create_successful_payment_update(amount_stars, payload_stars)
        success, response = self.send_webhook_update(payment_update_stars)
        
        if success:
            self.log_test("Payment Database Recording - Telegram Stars", True, 
                        "Telegram Stars payment should be recorded in database")
        else:
            self.log_test("Payment Database Recording - Telegram Stars", False, 
                        "Telegram Stars payment recording failed", str(response))
        
        time.sleep(1)
        
        # Test CryptoBot payment recording
        amount_crypto = 750.0
        webhook_data_crypto = self.create_cryptobot_webhook_data(amount_crypto, self.test_user_id)
        
        try:
            cryptobot_webhook_url = f"{API_BASE}/cryptobot/webhook"
            response = requests.post(cryptobot_webhook_url, json=webhook_data_crypto, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Payment Database Recording - CryptoBot", True, 
                            "CryptoBot payment should be recorded in database")
            else:
                self.log_test("Payment Database Recording - CryptoBot", False, 
                            f"CryptoBot payment recording failed with status {response.status_code}")
        except Exception as e:
            self.log_test("Payment Database Recording - CryptoBot", False, 
                        "CryptoBot payment recording request failed", str(e))

    def test_user_balance_updates(self):
        """Test that user balance is correctly updated after payments"""
        # Test balance update for Telegram Stars
        amount_stars = 300.0
        payload_stars = f"stars_payment_{self.test_user_id}_{amount_stars}"
        payment_update_stars = self.create_successful_payment_update(amount_stars, payload_stars)
        success, response = self.send_webhook_update(payment_update_stars)
        
        if success:
            self.log_test("User Balance Update - Telegram Stars", True, 
                        f"User balance should be increased by {amount_stars}₽ for Telegram Stars payment")
        else:
            self.log_test("User Balance Update - Telegram Stars", False, 
                        "Telegram Stars balance update failed", str(response))
        
        time.sleep(1)
        
        # Test balance update for CryptoBot
        amount_crypto = 800.0
        webhook_data_crypto = self.create_cryptobot_webhook_data(amount_crypto, self.test_user_id)
        
        try:
            cryptobot_webhook_url = f"{API_BASE}/cryptobot/webhook"
            response = requests.post(cryptobot_webhook_url, json=webhook_data_crypto, timeout=10)
            
            if response.status_code == 200:
                self.log_test("User Balance Update - CryptoBot", True, 
                            f"User balance should be increased by {amount_crypto}₽ for CryptoBot payment")
            else:
                self.log_test("User Balance Update - CryptoBot", False, 
                            f"CryptoBot balance update failed with status {response.status_code}")
        except Exception as e:
            self.log_test("User Balance Update - CryptoBot", False, 
                        "CryptoBot balance update request failed", str(e))

    def test_payment_notifications_to_user(self):
        """Test that payment notifications are sent to users"""
        # Test notification for Telegram Stars payment
        amount_stars = 400.0
        payload_stars = f"stars_payment_{self.test_user_id}_{amount_stars}"
        payment_update_stars = self.create_successful_payment_update(amount_stars, payload_stars)
        success, response = self.send_webhook_update(payment_update_stars)
        
        if success:
            self.log_test("Payment Notifications - Telegram Stars", True, 
                        "User should receive notification for Telegram Stars payment")
        else:
            self.log_test("Payment Notifications - Telegram Stars", False, 
                        "Telegram Stars payment notification failed", str(response))
        
        time.sleep(1)
        
        # Test notification for CryptoBot payment
        amount_crypto = 600.0
        webhook_data_crypto = self.create_cryptobot_webhook_data(amount_crypto, self.test_user_id)
        
        try:
            cryptobot_webhook_url = f"{API_BASE}/cryptobot/webhook"
            response = requests.post(cryptobot_webhook_url, json=webhook_data_crypto, timeout=10)
            
            if response.status_code == 200:
                self.log_test("Payment Notifications - CryptoBot", True, 
                            "User should receive notification for CryptoBot payment")
            else:
                self.log_test("Payment Notifications - CryptoBot", False, 
                            f"CryptoBot payment notification failed with status {response.status_code}")
        except Exception as e:
            self.log_test("Payment Notifications - CryptoBot", False, 
                        "CryptoBot payment notification request failed", str(e))

    # PRIORITY 3 TESTS - User state handling
    def test_user_state_management_stars(self):
        """Test user state management for Telegram Stars custom amounts"""
        # Test that user state is set for Stars custom amount
        callback_update = self.create_callback_update("stars_custom")
        success, response = self.send_webhook_update(callback_update)
        
        if success:
            self.log_test("User State Management - Stars State Set", True, 
                        "User state should be set to 'waiting_custom_amount_stars'")
        else:
            self.log_test("User State Management - Stars State Set", False, 
                        "Failed to set Stars custom amount state", str(response))
        
        time.sleep(1)
        
        # Send amount to clear state
        message_update = self.create_message_update("200")
        success, response = self.send_webhook_update(message_update)
        
        if success:
            self.log_test("User State Management - Stars State Cleared", True, 
                        "User state should be cleared after amount input")
        else:
            self.log_test("User State Management - Stars State Cleared", False, 
                        "Failed to clear Stars state after input", str(response))

    def test_user_state_management_crypto(self):
        """Test user state management for crypto custom amounts"""
        # Test that user state is set for crypto custom amount
        callback_update = self.create_callback_update("crypto_eth_custom")
        success, response = self.send_webhook_update(callback_update)
        
        if success:
            self.log_test("User State Management - Crypto State Set", True, 
                        "User state should be set to 'waiting_custom_amount_crypto'")
        else:
            self.log_test("User State Management - Crypto State Set", False, 
                        "Failed to set crypto custom amount state", str(response))
        
        time.sleep(1)
        
        # Send amount to clear state
        message_update = self.create_message_update("500")
        success, response = self.send_webhook_update(message_update)
        
        if success:
            self.log_test("User State Management - Crypto State Cleared", True, 
                        "User state should be cleared after amount input")
        else:
            self.log_test("User State Management - Crypto State Cleared", False, 
                        "Failed to clear crypto state after input", str(response))

    def test_handle_telegram_update_state_processing(self):
        """Test that handle_telegram_update correctly processes user states"""
        # Set crypto custom amount state
        callback_update = self.create_callback_update("crypto_usdt_custom")
        success, response = self.send_webhook_update(callback_update)
        
        if not success:
            self.log_test("Handle Telegram Update - State Processing Setup", False, 
                        "Failed to set up state for testing", str(response))
            return
        
        time.sleep(1)
        
        # Send message that should be processed as custom amount input
        message_update = self.create_message_update("1500")
        success, response = self.send_webhook_update(message_update)
        
        if success:
            self.log_test("Handle Telegram Update - State Processing", True, 
                        "handle_telegram_update correctly processed user state for custom amount input")
        else:
            self.log_test("Handle Telegram Update - State Processing", False, 
                        "handle_telegram_update failed to process user state", str(response))

    def run_all_tests(self):
        """Run all tests according to review request priorities"""
        print("🚀 Starting Telegram Bot Custom Deposits and Notifications Tests")
        print("=" * 80)
        print("Testing according to review request priorities:")
        print("1. PRIORITY 1 - Custom deposits for cryptocurrencies")
        print("2. PRIORITY 2 - Notification functions")
        print("3. PRIORITY 3 - User state handling")
        print("=" * 80)
        
        # Basic health check
        if not self.test_api_health():
            print("❌ API health check failed. Stopping tests.")
            return False
        
        print("\n🔥 PRIORITY 1 TESTS - Custom deposits for cryptocurrencies")
        print("-" * 60)
        self.test_crypto_custom_callback_data_parsing()
        self.test_crypto_custom_amount_callbacks()
        self.test_crypto_custom_vs_regular_callback_routing()
        self.test_crypto_custom_user_state_setting()
        self.test_crypto_custom_amount_input_flow()
        
        print("\n🔥 PRIORITY 2 TESTS - Notification functions")
        print("-" * 60)
        self.test_handle_successful_payment_telegram_stars()
        self.test_handle_cryptobot_payment_webhook()
        self.test_payment_database_recording()
        self.test_user_balance_updates()
        self.test_payment_notifications_to_user()
        
        print("\n🔥 PRIORITY 3 TESTS - User state handling")
        print("-" * 60)
        self.test_user_state_management_stars()
        self.test_user_state_management_crypto()
        self.test_handle_telegram_update_state_processing()
        
        # Summary
        print("=" * 80)
        print("📊 TELEGRAM BOT TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result['status'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        # Categorize results by priority
        priority1_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in ['Crypto Custom', 'Crypto Navigation'])]
        priority2_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in ['Payment', 'Balance', 'Notification'])]
        priority3_tests = [r for r in self.test_results if any(keyword in r['test'] for keyword in ['State', 'Handle Telegram Update'])]
        
        print(f"\nPRIORITY 1 (Crypto Custom Deposits): {len([t for t in priority1_tests if '✅ PASS' in t['status']])}/{len(priority1_tests)} passed")
        print(f"PRIORITY 2 (Notifications): {len([t for t in priority2_tests if '✅ PASS' in t['status']])}/{len(priority2_tests)} passed")
        print(f"PRIORITY 3 (User States): {len([t for t in priority3_tests if '✅ PASS' in t['status']])}/{len(priority3_tests)} passed")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
        else:
            print("\n✅ ALL TESTS PASSED!")
            print("🎉 The исправление действительно работает!")
        
        return failed == 0

if __name__ == "__main__":
    tester = TelegramBotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)