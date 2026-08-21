import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Tuple, List
from config import AgentConfig

class TelemetrySender:
    def __init__(self, backend_url: str = AgentConfig.BACKEND_URL):
        self.backend_url = backend_url
        self.session = requests.Session()
        self.offline_queue: List[Dict[str, Any]] = []

        retries = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "StudIQ-DesktopAgent/1.0 (Windows 11 x64)"
        })

    def send_telemetry(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Dispatches telemetry. If offline, queues payload and attempts batch flush on reconnection."""
        try:
            res = self.session.post(self.backend_url, json=payload, timeout=4.0)
            if res.status_code in (200, 201):
                # Flushed queued offline items if any exist
                self.flush_offline_queue()
                try:
                    return True, res.json()
                except Exception:
                    return True, {}
            else:
                print(f"[Agent Sender] Server returned status {res.status_code}. Queueing payload offline.")
                self.queue_offline_payload(payload)
                return False, {}
        except requests.RequestException as err:
            print(f"[Agent Sender] Offline / Connection Error ({err}). Queueing telemetry payload offline.")
            self.queue_offline_payload(payload)
            return False, {}

    def queue_offline_payload(self, payload: Dict[str, Any]):
        if len(self.offline_queue) < 1000:
            self.offline_queue.append(payload)

    def flush_offline_queue(self):
        if not self.offline_queue:
            return
        
        print(f"[Agent Queue] Reconnected! Flushing {len(self.offline_queue)} offline telemetry records...")
        to_flush = list(self.offline_queue)
        self.offline_queue.clear()

        for queued_item in to_flush:
            try:
                self.session.post(self.backend_url, json=queued_item, timeout=3.0)
            except Exception:
                # Re-queue remaining if connection drops again mid-flush
                self.offline_queue.append(queued_item)

    def send_popup_action(self, student_id: int, action: str) -> bool:
        """Sends popup response action to backend."""
        try:
            url = self.backend_url.replace("/monitoring/telemetry", "/monitoring/popup-action").replace("/monitoring/update", "/monitoring/popup-action")
            res = self.session.post(url, json={"student_id": student_id, "action": action}, timeout=5.0)
            return res.status_code == 200
        except Exception:
            return False

