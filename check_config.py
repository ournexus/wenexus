#!/usr/bin/env python3
"""Check and update database config"""
import psycopg2
import sys

conn = psycopg2.connect(
    dbname="wenexus_dev",
    user="wenexus",
    password="wenexus_dev_pwd",
    host="localhost",
    port="5432"
)

cur = conn.cursor()

# Check current config
try:
    cur.execute("SELECT name, value FROM config WHERE name = 'email_verification_enabled'")
    result = cur.fetchone()
    if result:
        print(f"Current config: {result[0]} = {result[1]}")
    else:
        print("Config 'email_verification_enabled' does not exist")
        print("Setting to 'false'...")
        cur.execute("INSERT INTO config (name, value) VALUES (%s, %s)",
                   ('email_verification_enabled', 'false'))
        conn.commit()
        print("✅ Set email_verification_enabled = false")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Check if resend_api_key is configured (email verification requires both)
try:
    cur.execute("SELECT name, value FROM config WHERE name = 'resend_api_key'")
    result = cur.fetchone()
    if result:
        api_key_value = result[1]
        if api_key_value:
            print(f"⚠️  resend_api_key is configured: {api_key_value[:10]}...")
        else:
            print("✅ resend_api_key is empty (good - email verification won't trigger)")
    else:
        print("✅ resend_api_key config does not exist (good - email verification won't trigger)")
except Exception as e:
    print(f"Error checking resend_api_key: {e}")

cur.close()
conn.close()
print("\n✅ Database check complete")
