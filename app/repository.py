from app.db import get_connection

def load_payload_map(dictionary_name: str):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT marker_id, payload_type, payload
            FROM markers
            WHERE dictionary_name = %s
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

from app.models.Marker_info import Marker_info

def get_all_markers() -> list[Marker_info]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT dictionary_name, marker_id, payload_type, payload
            FROM markers
            ORDER BY dictionary_name, marker_id
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [
        Marker_info(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )
        for row in rows]
    finally:
        cursor.close()
        conn.close()