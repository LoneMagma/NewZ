from database import get_connection

conn = get_connection()
conn.execute("""
    UPDATE articles
    SET relevance_score = 0,
        relevance_reason = NULL,
        sector_score = 0,
        geo_score = 0,
        urgency_score = 0
""")
conn.commit()
conn.close()
print("All scores reset.")