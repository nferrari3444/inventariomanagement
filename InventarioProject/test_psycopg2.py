# test_psycopg2.py
import psycopg2
import traceback

# Replace these with your actual values from Django settings
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': '5432',
    'database': 'filsadb_dev',  # Replace
    'user': 'filsa_dev',           # Replace
    'password': 'Filsa.2024'        # Replace
}

print("Testing psycopg2 connection with:")
print(f"Host: {DB_CONFIG['host']}")
print(f"Port: {DB_CONFIG['port']}")
print(f"Database: {DB_CONFIG['database']}")
print(f"User: {DB_CONFIG['user']}")
print("Password: [hidden]")
print("-" * 40)

try:
    # Test connection
    conn = psycopg2.connect(**DB_CONFIG)
    print("✅ psycopg2 connection successful!")

    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ Query successful: {version}")

    cursor.close()
    conn.close()
    print("✅ Connection closed successfully")

except Exception as e:
    print(f"❌ Connection failed: {type(e).__name__}")
    print(f"❌ Error message: {str(e)}")
    print("❌ Full traceback:")
    traceback.print_exc()