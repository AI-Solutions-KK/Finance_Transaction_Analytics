# Path: tools/cleanup_utils.py

import os
import shutil
from sqlalchemy import text
from database.db_engine import SessionLocal


def cleanup_session_data(session_id=None, cleanup_all=False):
    """
    Cleans up database records and file system for a session.

    Args:
        session_id: Specific session to clean (optional)
        cleanup_all: If True, cleans ALL data (use for fresh start)

    Returns:
        tuple: (success: bool, message: str)
    """
    db = SessionLocal()

    try:
        # 1. DATABASE CLEANUP
        if cleanup_all:
            # Delete all records from fact table
            result = db.execute(
                text("DELETE FROM C##FINANCE.FACT_TRANSACTIONS")
            )
            deleted_count = result.rowcount
            db.commit()
            print(f"✅ Deleted {deleted_count} records from database")

        elif session_id:
            # Delete specific session records
            result = db.execute(
                text("DELETE FROM C##FINANCE.FACT_TRANSACTIONS WHERE session_id = :sid"),
                {"sid": session_id}
            )
            deleted_count = result.rowcount
            db.commit()
            print(f"✅ Deleted {deleted_count} records for session: {session_id}")

        # 2. FILE SYSTEM CLEANUP
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        uploaded_data_dir = os.path.join(BASE_DIR, "uploaded_data")

        if cleanup_all:
            # Remove all session folders
            if os.path.exists(uploaded_data_dir):
                shutil.rmtree(uploaded_data_dir)
                os.makedirs(uploaded_data_dir, exist_ok=True)
                print(f"✅ Cleaned all uploaded data folders")

        elif session_id:
            # Remove specific session folder
            session_folder = os.path.join(uploaded_data_dir, session_id)
            if os.path.exists(session_folder):
                shutil.rmtree(session_folder)
                print(f"✅ Removed folder: {session_folder}")

        return True, "Cleanup completed successfully"

    except Exception as e:
        db.rollback()
        print(f"❌ Cleanup failed: {e}")
        return False, f"Cleanup failed: {str(e)}"

    finally:
        db.close()


def cleanup_old_sessions(days_old=7):
    """
    Cleanup sessions older than specified days.
    Useful for periodic maintenance.

    Args:
        days_old: Remove sessions older than this many days
    """
    db = SessionLocal()

    try:
        # Delete old records (based on created_at timestamp)
        result = db.execute(
            text("""
                 DELETE
                 FROM C##FINANCE.FACT_TRANSACTIONS
                 WHERE created_at < SYSDATE - :days
                 """),
            {"days": days_old}
        )
        deleted_count = result.rowcount
        db.commit()

        print(f"✅ Deleted {deleted_count} old records (>{days_old} days)")
        return True, f"Removed {deleted_count} old records"

    except Exception as e:
        db.rollback()
        return False, f"Old session cleanup failed: {str(e)}"

    finally:
        db.close()


def get_active_sessions():
    """
    Returns list of session IDs currently in database.
    Useful for debugging.
    """
    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                 SELECT DISTINCT session_id,
                                 COUNT(*)        as record_count,
                                 MIN(created_at) as first_upload,
                                 MAX(created_at) as last_upload
                 FROM C##FINANCE.FACT_TRANSACTIONS
                 GROUP BY session_id
                 ORDER BY last_upload DESC
                 """)
        )

        sessions = []
        for row in result:
            sessions.append({
                "session_id": row[0],
                "record_count": row[1],
                "first_upload": row[2],
                "last_upload": row[3]
            })

        return sessions

    except Exception as e:
        print(f"❌ Failed to get active sessions: {e}")
        return []

    finally:
        db.close()