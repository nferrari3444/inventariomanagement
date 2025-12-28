import psycopg2

try:
    conn = psycopg2.connect(
        dbname="filsadb_dev",
        user="filsa_dev",
        host="127.0.0.1",
        port="5432"
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {type(e).__name__}: {e}")

# Also try with localhost
try:
    conn = psycopg2.connect(
        dbname="filsadb_dev",
        user="filsa_dev",
        host="127.0.0.1",
        port="5432"
    )
    print("Connection successful with localhost!")
    conn.close()
except Exception as e:
    print(f"Connection failed with localhost: {type(e).__name__}: {e}")