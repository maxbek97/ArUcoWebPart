from app.db import get_connection
from app.models.Marker_info import MarkerInfoDTO
from psycopg2.extras import Json
import os
import shutil
from fastapi import UploadFile, HTTPException

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

        # print(f"[load_payload_map] loaded {len(payload_map)} markers for {dictionary_name}")
        return payload_map
    finally:
        cursor.close()
        conn.close()


def get_all_markers(dict_name: str | None = None) -> list[MarkerInfoDTO]:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if dict_name:
            query = """
                SELECT dictionary_name, marker_id, payload_type, payload
                FROM markers
                WHERE dictionary_name = %s
                ORDER BY marker_id
            """
            cursor.execute(query, (dict_name,))
        else:
            query = """
                SELECT dictionary_name, marker_id, payload_type, payload
                FROM markers
                ORDER BY dictionary_name, marker_id
            """
            cursor.execute(query)
            
        rows = cursor.fetchall()
        return [
        MarkerInfoDTO(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )
        for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_marker(dict_name: str, marker_id: int) -> MarkerInfoDTO:
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
        conn.commit()

        if row is None:
            return None

        return MarkerInfoDTO(
            dictionary_name=row[0],
            marker_id=row[1],
            payload_type=row[2],
            payload=row[3]
        )

    finally:
        cursor.close()
        conn.close()


def add_new_marker_info(marker_info: MarkerInfoDTO) -> MarkerInfoDTO:
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

        return MarkerInfoDTO(
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


def update_marker_info(marker: MarkerInfoDTO) -> MarkerInfoDTO:
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
        conn.commit()

        if row is None:
            return None

        return MarkerInfoDTO(
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


def delete_marker(dict_name: str, marker_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            DELETE FROM markers
            WHERE dictionary_name = %s
              AND marker_id = %s
            RETURNING dictionary_name, marker_id, payload_type, payload 
        """
        cursor.execute(
            query, 
            (
                dict_name, 
                marker_id
            )
        )
        row = cursor.fetchone()
        conn.commit()
        if row is None:
            return None
        
        return MarkerInfoDTO(
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