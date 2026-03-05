from database import get_connection, init_db

init_db()

conn = get_connection()
conn.execute("""
    INSERT OR REPLACE INTO user_profile
        (id, role, location, sectors, watching, sensitivity)
    VALUES (1, 'student investor', 'India', 'tech, pharma, manufacturing',
            'RBI policy, US-India trade, Nifty', 5)
""")
conn.commit()
conn.close()
print("Profile created.")
