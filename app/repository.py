from app.db import get_connection
from app.models.Marker_info import Marker_info
from psycopg2.extras import Json
from fastapi import HTTPException

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

def get_marker(dict_name: str, marker_id: int) -> Marker_info:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            SELECT dictionary_name, marker_id, payload_type, payload
            FROM markers
            WHERE dictionary_name = %s AND marker_id = %s
        """
        cursor.execute(
            query,
                (
                    dict_name,
                    marker_id
                )
            )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
        status_code=404,
        detail="Marker not found"
    )
        return Marker_info(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )

    finally:
        cursor.close()
        conn.close()


def add_new_marker_info(marker_info: Marker_info):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO markers (dictionary_name, marker_id, payload_type, payload)
            VALUES (%s, %s, %s, %s)
            RETURNING dictionary_name, marker_id, payload_type, payload
        """
        cursor.execute(
            query,
            (
                marker_info.dictionary_name,
                marker_info.marker_id,
                marker_info.payload_type,
                Json(marker_info.payload)
            )
        )
        row = cursor.fetchone()
        conn.commit()

        return Marker_info(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


def update_marker_info(marker: Marker_info) -> Marker_info:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            UPDATE markers
            SET payload_type = %s,
                payload = %s
            WHERE dictionary_name = %s
                AND marker_id = %s
            RETURNING dictionary_name, marker_id, payload_type, payload
        """

        cursor.execute(
            query,
            (
                marker.payload_type,
                Json(marker.payload),  # 🔥 не забываем
                marker.dictionary_name,
                marker.marker_id
            )
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Marker not found"
            )

        conn.commit()

        return Marker_info(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()