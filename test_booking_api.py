#!/usr/bin/env python3
"""Test booking API endpoints"""
import requests
import sys

# Login to get token
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    sys.exit(1)

token = login_response.json()["access_token"]
print(f"✅ Got token: {token[:50]}...")

# Test bookings calendar endpoint
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/bookings/calendar/public-holidays/2025",
    headers=headers
)

print(f"\n📡 GET /api/v1/bookings/calendar/public-holidays/2025")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

if response.status_code == 200:
    print("✅ SUCCESS!")
else:
    print("❌ FAILED!")
