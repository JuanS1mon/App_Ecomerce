#!/usr/bin/env python3
# Test script to simulate exact browser headers for debugging login issues

import requests
import json

def test_login_with_browser_headers():
    """
    Test login endpoint with headers that exactly match what a browser would send
    """
    url = "http://localhost:8000/login"
    
    # Headers that a real browser would send
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'localhost:8000',
        'Origin': 'http://localhost:8000',
        'Pragma': 'no-cache',
        'Referer': 'http://localhost:8000/static/login_isolated.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    # Test data
    data = {
        'username': 'testuser',
        'password': 'Test123456'
    }
    
    print("🔍 Testing login with exact browser headers...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {data}")
    print("-" * 50)
    
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                print(f"📄 Response JSON: {json.dumps(response_json, indent=2)}")
                
                # Verify token exists
                if 'access_token' in response_json:
                    print("✅ Login successful - JWT token received")
                    print(f"🔑 Token: {response_json['access_token'][:50]}...")
                else:
                    print("❌ Login response missing access_token")
                    
            except json.JSONDecodeError:
                print(f"📄 Response Text: {response.text}")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 Request failed: {e}")
    
    print("\n" + "="*60)

def test_preflight_options():
    """
    Test OPTIONS request that browsers send for CORS preflight
    """
    url = "http://localhost:8000/login"
    
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Access-Control-Request-Headers': 'content-type',
        'Access-Control-Request-Method': 'POST',
        'Connection': 'keep-alive',
        'Host': 'localhost:8000',
        'Origin': 'http://localhost:8000',
        'Referer': 'http://localhost:8000/static/login_isolated.html',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 Testing CORS preflight OPTIONS request...")
    print(f"URL: {url}")
    print(f"Method: OPTIONS")
    
    try:
        response = requests.options(url, headers=headers, timeout=10)
        
        print(f"✅ Status Code: {response.status_code}")
        print(f"📋 Response Headers: {dict(response.headers)}")
        
        # Check CORS headers
        cors_headers = {k: v for k, v in response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print(f"🌐 CORS Headers: {json.dumps(cors_headers, indent=2)}")
        else:
            print("❌ No CORS headers found")
            
    except requests.exceptions.RequestException as e:
        print(f"💥 OPTIONS request failed: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🚀 Browser Headers Login Test")
    print("="*60)
    
    # Test CORS preflight first
    test_preflight_options()
    
    # Then test actual login
    test_login_with_browser_headers()
    
    print("🏁 Test completed")
