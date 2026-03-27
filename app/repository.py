from app.db import get_connection

def load_payload_map(dictionary_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT m.marker_id, m.payload_type, m.payload
            FROM markers m
            JOIN dictionaries d ON d.id = m.dictionary_id
            WHERE d.name = %s
        """

        cursor.execute(query, (dictionary_name,))
        rows = cursor.fetchall()

        payload_map = {}

        for marker_id, p_type, payload in rows:
            payload_map[marker_id] = {
                "type": p_type,
                "value": payload
            }

        cursor.close()
        conn.close()

        return payload_map
    finally:
        cursor.close()
        conn.close()