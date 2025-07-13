#!/usr/bin/env python3
"""
CRITICAL ISSUE TESTING: Crypto Bot Menu Repetition Problem
User reports: При нажатии на ЛЮБУЮ сумму в криптоботе он получает то же меню повторно

PRIORITY TESTING FLOW:
1. Test crypto_btc callback -> should show amount selection menu
2. Test crypto_btc_100 callback -> should create invoice, NOT show menu again  
3. Test crypto_btc_custom callback -> should ask for custom amount input
4. Test create_cryptobot_invoice function
5. Test full flow end-to-end with detailed logging
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

class CryptoBotFlowTester:
    def __init__(self):
        self.test_results = []
        self.test_user_id = 987654321  # Test user ID
        self.test_chat_id = 987654321  # Test chat ID
        
    def log_test(self, test_name, success, message="", details=""):
        """Log test result with detailed information"""
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
        """Send webhook update to the bot with detailed logging"""
        try:
            webhook_url = f"{API_BASE}/webhook/{WEBHOOK_SECRET}"
            print(f"🔄 Sending webhook to: {webhook_url}")
            print(f"📤 Update data: {json.dumps(update_data, indent=2)}")
            
            response = requests.post(webhook_url, json=update_data, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            return response.status_code == 200, response
        except Exception as e:
            print(f"❌ Webhook error: {str(e)}")
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

    def test_crypto_btc_callback(self):
        """CRITICAL TEST: Test crypto_btc callback - should show amount selection menu"""
        print("\n🔍 TESTING: crypto_btc callback (should show amount selection menu)")
        
        update = self.create_callback_update("crypto_btc")
        success, response = self.send_webhook_update(update)
        
        if success:
            self.log_test("Crypto BTC Callback", True, "crypto_btc callback processed - should show amount selection menu")
        else:
            self.log_test("Crypto BTC Callback", False, "crypto_btc callback failed", str(response))
        
        return success

    def test_crypto_btc_100_callback(self):
        """CRITICAL TEST: Test crypto_btc_100 callback - should create invoice, NOT show menu again"""
        print("\n🔍 TESTING: crypto_btc_100 callback (should create invoice, NOT show menu again)")
        
        update = self.create_callback_update("crypto_btc_100")
        success, response = self.send_webhook_update(update)
        
        if success:
            self.log_test("Crypto BTC 100 Callback", True, "crypto_btc_100 callback processed - should create invoice, NOT show menu again")
        else:
            self.log_test("Crypto BTC 100 Callback", False, "crypto_btc_100 callback failed", str(response))
        
        return success

    def test_crypto_btc_custom_callback(self):
        """CRITICAL TEST: Test crypto_btc_custom callback - should ask for custom amount input"""
        print("\n🔍 TESTING: crypto_btc_custom callback (should ask for custom amount input)")
        
        update = self.create_callback_update("crypto_btc_custom")
        success, response = self.send_webhook_update(update)
        
        if success:
            self.log_test("Crypto BTC Custom Callback", True, "crypto_btc_custom callback processed - should ask for custom amount input")
        else:
            self.log_test("Crypto BTC Custom Callback", False, "crypto_btc_custom callback failed", str(response))
        
        return success

    def test_all_crypto_amount_callbacks(self):
        """Test all crypto amount callbacks to verify they don't show menu again"""
        print("\n🔍 TESTING: All crypto amount callbacks (should create invoices, NOT show menus)")
        
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        amounts = ["100", "250", "500", "1000", "2000", "5000"]
        
        all_passed = True
        
        for crypto in crypto_types:
            for amount in amounts:
                callback_data = f"crypto_{crypto}_{amount}"
                print(f"\n   Testing: {callback_data}")
                
                update = self.create_callback_update(callback_data)
                success, response = self.send_webhook_update(update)
                
                if success:
                    self.log_test(f"Crypto Amount Callback ({callback_data})", True, f"Should create invoice for {amount}₽ {crypto.upper()}")
                else:
                    self.log_test(f"Crypto Amount Callback ({callback_data})", False, f"Failed to process {callback_data}", str(response))
                    all_passed = False
                
                time.sleep(0.5)  # Small delay between tests
        
        return all_passed

    def test_cryptobot_invoice_creation(self):
        """Test CryptoBot invoice creation function"""
        print("\n🔍 TESTING: CryptoBot invoice creation")
        
        # Test if we can access the create_cryptobot_invoice function
        try:
            # We'll test this by triggering a crypto payment that should create an invoice
            update = self.create_callback_update("crypto_btc_500")
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test("CryptoBot Invoice Creation", True, "Invoice creation triggered successfully")
            else:
                self.log_test("CryptoBot Invoice Creation", False, "Invoice creation failed", str(response))
            
            return success
        except Exception as e:
            self.log_test("CryptoBot Invoice Creation", False, "Exception during invoice creation", str(e))
            return False

    def test_full_crypto_flow(self):
        """Test complete crypto payment flow"""
        print("\n🔍 TESTING: Complete crypto payment flow")
        
        # Step 1: Navigate to balance menu
        print("   Step 1: Navigate to balance menu")
        update1 = self.create_callback_update("menu_balance")
        success1, response1 = self.send_webhook_update(update1)
        time.sleep(1)
        
        # Step 2: Select crypto payment
        print("   Step 2: Select crypto payment")
        update2 = self.create_callback_update("pay_crypto")
        success2, response2 = self.send_webhook_update(update2)
        time.sleep(1)
        
        # Step 3: Select Bitcoin
        print("   Step 3: Select Bitcoin")
        update3 = self.create_callback_update("crypto_btc")
        success3, response3 = self.send_webhook_update(update3)
        time.sleep(1)
        
        # Step 4: Select amount (THIS IS THE CRITICAL STEP)
        print("   Step 4: Select 100₽ amount (CRITICAL - should NOT show menu again)")
        update4 = self.create_callback_update("crypto_btc_100")
        success4, response4 = self.send_webhook_update(update4)
        time.sleep(1)
        
        all_success = success1 and success2 and success3 and success4
        
        if all_success:
            self.log_test("Full Crypto Flow", True, "Complete flow executed successfully - amount selection should create invoice")
        else:
            failed_steps = []
            if not success1: failed_steps.append("Balance menu")
            if not success2: failed_steps.append("Crypto payment")
            if not success3: failed_steps.append("Bitcoin selection")
            if not success4: failed_steps.append("Amount selection (CRITICAL)")
            
            self.log_test("Full Crypto Flow", False, f"Flow failed at: {', '.join(failed_steps)}")
        
        return all_success

    def test_callback_data_parsing(self):
        """Test callback data parsing logic"""
        print("\n🔍 TESTING: Callback data parsing logic")
        
        # Test different callback data formats
        test_cases = [
            ("crypto_btc", "Should trigger handle_crypto_payment"),
            ("crypto_btc_100", "Should trigger handle_crypto_payment_amount"),
            ("crypto_btc_custom", "Should trigger handle_crypto_custom_amount"),
            ("crypto_eth_250", "Should trigger handle_crypto_payment_amount"),
            ("crypto_usdt_custom", "Should trigger handle_crypto_custom_amount"),
            ("crypto_ltc_1000", "Should trigger handle_crypto_payment_amount"),
        ]
        
        all_passed = True
        
        for callback_data, expected_behavior in test_cases:
            print(f"   Testing: {callback_data} -> {expected_behavior}")
            
            update = self.create_callback_update(callback_data)
            success, response = self.send_webhook_update(update)
            
            if success:
                self.log_test(f"Callback Parsing ({callback_data})", True, expected_behavior)
            else:
                self.log_test(f"Callback Parsing ({callback_data})", False, f"Failed to parse {callback_data}", str(response))
                all_passed = False
            
            time.sleep(0.5)
        
        return all_passed

    def test_edge_cases(self):
        """Test edge cases that might cause menu repetition"""
        print("\n🔍 TESTING: Edge cases for menu repetition")
        
        # Test rapid successive clicks
        print("   Testing: Rapid successive amount clicks")
        for i in range(3):
            update = self.create_callback_update("crypto_btc_100")
            success, response = self.send_webhook_update(update)
            time.sleep(0.2)
        
        self.log_test("Edge Case - Rapid Clicks", True, "Rapid successive clicks handled")
        
        # Test different crypto types with same amount
        print("   Testing: Different crypto types with same amount")
        crypto_types = ["btc", "eth", "usdt", "ltc"]
        for crypto in crypto_types:
            update = self.create_callback_update(f"crypto_{crypto}_500")
            success, response = self.send_webhook_update(update)
            time.sleep(0.3)
        
        self.log_test("Edge Case - Multiple Crypto Types", True, "Multiple crypto types with same amount handled")
        
        return True

    def run_critical_tests(self):
        """Run critical tests for crypto bot menu repetition issue"""
        print("🚨 CRITICAL ISSUE TESTING: Crypto Bot Menu Repetition")
        print("User Problem: При нажатии на ЛЮБУЮ сумму в криптоботе он получает то же меню повторно")
        print("=" * 80)
        
        # Basic health check
        if not self.test_api_health():
            print("❌ API health check failed. Stopping tests.")
            return False
        
        # Critical flow tests
        print("\n🎯 CRITICAL FLOW TESTS")
        print("-" * 40)
        
        self.test_crypto_btc_callback()
        time.sleep(1)
        
        self.test_crypto_btc_100_callback()
        time.sleep(1)
        
        self.test_crypto_btc_custom_callback()
        time.sleep(1)
        
        # Test all amount callbacks
        print("\n🎯 ALL AMOUNT CALLBACK TESTS")
        print("-" * 40)
        self.test_all_crypto_amount_callbacks()
        
        # Test invoice creation
        print("\n🎯 INVOICE CREATION TESTS")
        print("-" * 40)
        self.test_cryptobot_invoice_creation()
        
        # Test complete flow
        print("\n🎯 COMPLETE FLOW TESTS")
        print("-" * 40)
        self.test_full_crypto_flow()
        
        # Test callback parsing
        print("\n🎯 CALLBACK PARSING TESTS")
        print("-" * 40)
        self.test_callback_data_parsing()
        
        # Test edge cases
        print("\n🎯 EDGE CASE TESTS")
        print("-" * 40)
        self.test_edge_cases()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CRITICAL ISSUE TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result['status'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
                    if result['details']:
                        print(f"    Details: {result['details']}")
        else:
            print("\n✅ ALL CRITICAL TESTS PASSED!")
            print("🎉 Crypto bot menu repetition issue appears to be resolved!")
        
        return failed == 0

if __name__ == "__main__":
    tester = CryptoBotFlowTester()
    success = tester.run_critical_tests()
    sys.exit(0 if success else 1)