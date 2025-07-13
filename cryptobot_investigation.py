#!/usr/bin/env python3
"""
DEEP INVESTIGATION: CryptoBot Invoice Creation Issue
Testing the actual CryptoBot API integration to find the root cause
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
CRYPTOBOT_TOKEN = os.getenv('CRYPTOBOT_TOKEN')
CRYPTOBOT_BASE_URL = os.getenv('CRYPTOBOT_BASE_URL')

class CryptoBotInvestigator:
    def __init__(self):
        self.test_results = []
        self.test_user_id = 987654321
        
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
        if details:
            print(f"   Details: {details}")
        print()

    def test_cryptobot_api_direct(self):
        """Test CryptoBot API directly"""
        print("🔍 TESTING: Direct CryptoBot API call")
        
        try:
            url = f"{CRYPTOBOT_BASE_URL}/createInvoice"
            headers = {
                "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
                "Content-Type": "application/json"
            }
            
            payload = {
                "currency_type": "fiat",
                "fiat": "RUB",
                "amount": "100",
                "description": f"Test invoice for user {self.test_user_id}",
                "paid_btn_name": "callback",
                "paid_btn_url": "https://t.me/search1_test_bot",
                "payload": f"test_payment_{self.test_user_id}_100"
            }
            
            print(f"🔄 Making request to: {url}")
            print(f"📤 Headers: {json.dumps(headers, indent=2)}")
            print(f"📤 Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    invoice_url = data.get('result', {}).get('bot_invoice_url')
                    invoice_id = data.get('result', {}).get('invoice_id')
                    
                    self.log_test("CryptoBot API Direct Call", True, 
                                f"Invoice created successfully. ID: {invoice_id}, URL: {invoice_url}")
                    return True
                else:
                    error_msg = data.get('error', {}).get('message', 'Unknown error')
                    self.log_test("CryptoBot API Direct Call", False, 
                                f"API returned error: {error_msg}", str(data))
                    return False
            else:
                self.log_test("CryptoBot API Direct Call", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("CryptoBot API Direct Call", False, 
                        "Exception during API call", str(e))
            return False

    def test_cryptobot_token_validity(self):
        """Test if CryptoBot token is valid"""
        print("🔍 TESTING: CryptoBot token validity")
        
        try:
            url = f"{CRYPTOBOT_BASE_URL}/getMe"
            headers = {
                "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN,
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    app_name = data.get('result', {}).get('name', 'Unknown')
                    self.log_test("CryptoBot Token Validity", True, 
                                f"Token is valid. App name: {app_name}")
                    return True
                else:
                    self.log_test("CryptoBot Token Validity", False, 
                                "Token validation failed", str(data))
                    return False
            else:
                self.log_test("CryptoBot Token Validity", False, 
                            f"HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("CryptoBot Token Validity", False, 
                        "Exception during token validation", str(e))
            return False

    def test_backend_crypto_flow_with_logging(self):
        """Test backend crypto flow with detailed logging"""
        print("🔍 TESTING: Backend crypto flow with detailed logging")
        
        # Create a callback update for crypto_btc_100
        update_data = {
            "update_id": int(time.time()),
            "callback_query": {
                "id": str(int(time.time())),
                "from": {
                    "id": self.test_user_id,
                    "is_bot": False,
                    "first_name": "TestUser",
                    "username": "testuser_investigation"
                },
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": 123456789,
                        "is_bot": True,
                        "first_name": "TestBot",
                        "username": "search1_test_bot"
                    },
                    "chat": {
                        "id": self.test_user_id,
                        "first_name": "TestUser",
                        "username": "testuser_investigation",
                        "type": "private"
                    },
                    "date": int(time.time()),
                    "text": "Test message"
                },
                "data": "crypto_btc_100"
            }
        }
        
        try:
            webhook_url = f"{API_BASE}/webhook/{WEBHOOK_SECRET}"
            print(f"🔄 Sending webhook to: {webhook_url}")
            print(f"📤 Update data: {json.dumps(update_data, indent=2)}")
            
            response = requests.post(webhook_url, json=update_data, timeout=30)
            
            print(f"📥 Response status: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
            if response.status_code == 200:
                self.log_test("Backend Crypto Flow", True, 
                            "Webhook processed successfully")
                return True
            else:
                self.log_test("Backend Crypto Flow", False, 
                            f"Webhook failed with HTTP {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Backend Crypto Flow", False, 
                        "Exception during webhook call", str(e))
            return False

    def test_environment_variables(self):
        """Test if all required environment variables are set"""
        print("🔍 TESTING: Environment variables")
        
        required_vars = {
            'CRYPTOBOT_TOKEN': CRYPTOBOT_TOKEN,
            'CRYPTOBOT_BASE_URL': CRYPTOBOT_BASE_URL,
            'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
            'WEBHOOK_SECRET': WEBHOOK_SECRET
        }
        
        all_set = True
        for var_name, var_value in required_vars.items():
            if var_value:
                print(f"✅ {var_name}: Set (length: {len(var_value)})")
            else:
                print(f"❌ {var_name}: Not set or empty")
                all_set = False
        
        if all_set:
            self.log_test("Environment Variables", True, "All required variables are set")
        else:
            self.log_test("Environment Variables", False, "Some required variables are missing")
        
        return all_set

    def check_backend_logs(self):
        """Check backend logs for any errors"""
        print("🔍 CHECKING: Backend logs for errors")
        
        try:
            # Check supervisor logs
            import subprocess
            result = subprocess.run(['tail', '-n', '50', '/var/log/supervisor/backend.out.log'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logs = result.stdout
                print("📋 Recent backend logs:")
                print(logs)
                
                # Look for errors
                error_keywords = ['error', 'exception', 'failed', 'traceback']
                errors_found = []
                
                for line in logs.lower().split('\n'):
                    for keyword in error_keywords:
                        if keyword in line:
                            errors_found.append(line)
                
                if errors_found:
                    self.log_test("Backend Logs Check", False, 
                                f"Found {len(errors_found)} potential errors", 
                                '\n'.join(errors_found))
                else:
                    self.log_test("Backend Logs Check", True, "No obvious errors in recent logs")
            else:
                self.log_test("Backend Logs Check", False, "Could not read backend logs")
                
        except Exception as e:
            self.log_test("Backend Logs Check", False, "Exception while checking logs", str(e))

    def run_investigation(self):
        """Run complete investigation"""
        print("🕵️ STARTING DEEP INVESTIGATION: CryptoBot Invoice Creation")
        print("=" * 80)
        
        # Test environment variables
        self.test_environment_variables()
        
        # Test CryptoBot token validity
        self.test_cryptobot_token_validity()
        
        # Test direct CryptoBot API call
        self.test_cryptobot_api_direct()
        
        # Test backend flow
        self.test_backend_crypto_flow_with_logging()
        
        # Check backend logs
        self.check_backend_logs()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 INVESTIGATION SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result['status'])
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result['status'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n❌ ISSUES FOUND:")
            for result in self.test_results:
                if "❌ FAIL" in result['status']:
                    print(f"  - {result['test']}: {result['message']}")
                    if result['details']:
                        print(f"    Details: {result['details']}")
        else:
            print("\n✅ NO ISSUES FOUND!")
            print("🤔 The CryptoBot integration appears to be working correctly.")
            print("💡 The user's issue might be related to:")
            print("   - Network connectivity on their end")
            print("   - Telegram client issues")
            print("   - Timing issues with message delivery")
            print("   - User interface confusion")
        
        return failed == 0

if __name__ == "__main__":
    investigator = CryptoBotInvestigator()
    success = investigator.run_investigation()
    sys.exit(0 if success else 1)