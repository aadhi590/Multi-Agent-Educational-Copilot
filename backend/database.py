import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

class FirebaseDB:
    def __init__(self):
        """Initialize Firebase with graceful degradation if credentials are missing."""
        self.db = None

        if firebase_admin._apps:
            # Already initialized (e.g., from a previous import)
            try:
                self.db = firestore.client()
            except Exception as e:
                print(f"[Firebase] Already initialized but Firestore unavailable: {e}")
            return

        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")

        if cred_path and os.path.exists(cred_path):
            try:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("[Firebase] Initialized successfully with service account.")
            except Exception as e:
                print(f"[Firebase] Failed to initialize with service account: {e}")
                print("[Firebase] Running WITHOUT database persistence.")
        else:
            print(f"[Firebase] Service account key not found at: {cred_path}")
            print("[Firebase] Running WITHOUT database persistence.")

    def _is_available(self) -> bool:
        return self.db is not None

    # ------------------------------------------------------------------
    # Session State
    # ------------------------------------------------------------------

    def get_student_session_state(self, student_id: str, session_id: str) -> dict:
        if not self._is_available():
            return {}
        try:
            doc_ref = (
                self.db.collection("students")
                .document(student_id)
                .collection("sessions")
                .document(session_id)
            )
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else {}
        except Exception as e:
            print(f"[Firebase] get_student_session_state error: {e}")
            return {}

    def save_student_session_state(self, student_id: str, session_id: str, state_data: dict):
        if not self._is_available():
            return
        try:
            # Firestore cannot store arbitrary Python objects; filter to safe types.
            safe_data = _sanitize_for_firestore(state_data)
            doc_ref = (
                self.db.collection("students")
                .document(student_id)
                .collection("sessions")
                .document(session_id)
            )
            doc_ref.set(safe_data, merge=True)
        except Exception as e:
            print(f"[Firebase] save_student_session_state error: {e}")

    # ------------------------------------------------------------------
    # Mastery Tracking
    # ------------------------------------------------------------------

    def update_mastery(self, student_id: str, topic: str, mastery_data: dict):
        if not self._is_available():
            return
        try:
            doc_ref = (
                self.db.collection("students")
                .document(student_id)
                .collection("mastery")
                .document(topic)
            )
            doc_ref.set(mastery_data, merge=True)
        except Exception as e:
            print(f"[Firebase] update_mastery error: {e}")

    def get_mastery(self, student_id: str) -> dict:
        if not self._is_available():
            return {}
        try:
            docs = (
                self.db.collection("students")
                .document(student_id)
                .collection("mastery")
                .stream()
            )
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            print(f"[Firebase] get_mastery error: {e}")
            return {}


def _sanitize_for_firestore(data: dict) -> dict:
    """Recursively convert AgentState to Firestore-safe types."""
    safe = {}
    for k, v in data.items():
        if k == "messages":
            # Store messages as list of plain dicts
            safe[k] = [
                {"role": getattr(m, "type", "unknown"), "content": getattr(m, "content", str(m))}
                if hasattr(m, "content") else {"role": "unknown", "content": str(m)}
                for m in v
            ]
        elif isinstance(v, dict):
            safe[k] = _sanitize_for_firestore(v)
        elif isinstance(v, list):
            safe[k] = [str(i) if not isinstance(i, (str, int, float, bool)) else i for i in v]
        elif isinstance(v, (str, int, float, bool)) or v is None:
            safe[k] = v
        else:
            safe[k] = str(v)
    return safe


# Singleton instance
db_manager = FirebaseDB()
