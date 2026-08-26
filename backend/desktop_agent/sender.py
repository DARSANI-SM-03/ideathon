import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Tuple, List
from config import AgentConfig

import os

import json
import os
import sys
import shutil

class TelemetrySender:
    def __init__(self, backend_url: str = ""):
        if not backend_url:
            backend_url = os.getenv("STUDIQ_BACKEND_URL", AgentConfig.BACKEND_URL)
        self.backend_url = backend_url
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "StudIQ-DesktopAgent/1.0 (Windows 11 x64)"
        }
        self.max_queue_size = 1000
        self.queue_file = self._get_queue_file_path()
        self.offline_queue: List[Dict[str, Any]] = self._load_queue_from_disk()

    def _get_queue_file_path(self) -> str:
        appdata = os.getenv("LOCALAPPDATA", os.path.dirname(os.path.abspath(__file__)))
        studiq_dir = os.path.join(appdata, "StudIQ")
        os.makedirs(studiq_dir, exist_ok=True)
        return os.path.join(studiq_dir, "offline_queue.json")

    def _load_queue_from_disk(self) -> List[Dict[str, Any]]:
        """Durable Queue Read: Loads offline queue from disk with corruption recovery."""
        if not os.path.exists(self.queue_file):
            return []
        try:
            with open(self.queue_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data[:self.max_queue_size]
        except Exception as e:
            print(f"[Agent Queue Warning] Queue file corruption detected ({e}). Backing up corrupted queue.")
            try:
                bak_file = self.queue_file + ".corrupted.bak"
                shutil.copy(self.queue_file, bak_file)
            except Exception:
                pass
        return []

    def _save_queue_to_disk(self):
        """Atomic Write Strategy: Writes queue to temporary file before atomic replace."""
        tmp_file = self.queue_file + ".tmp"
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(self.offline_queue[:self.max_queue_size], f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_file, self.queue_file)
        except Exception as e:
            print(f"[Agent Queue Error] Failed to persist queue to disk: {e}")

    def send_telemetry(self, payload: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Dispatches telemetry. Includes agent_token in headers if present."""
        token = os.getenv("STUDIQ_AGENT_TOKEN", "")
        target_url = os.getenv("STUDIQ_BACKEND_URL", self.backend_url)
        headers = dict(self.headers)
        if token:
            headers["Authorization"] = f"Bearer {token}"

        payload_to_send = dict(payload)
        if token:
            payload_to_send["agent_token"] = token

        try:
            print(f"[SENDER] POST {target_url}")
            res = requests.post(target_url, json=payload_to_send, headers=headers, timeout=5.0)
            print(f"[SENDER] HTTP {res.status_code}")
            if res.status_code in (200, 201):
                self.flush_offline_queue()
                try:
                    return True, res.json()
                except Exception:
                    return True, {}
            else:
                print(f"[SENDER] Server returned HTTP {res.status_code}. Queueing payload offline.")
                self.queue_offline_payload(payload_to_send)
                return False, {}
        except Exception as err:
            print(f"[SENDER] Connection error ({err}). Queueing telemetry payload offline.")
            self.queue_offline_payload(payload_to_send)
            return False, {}

    def queue_offline_payload(self, payload: Dict[str, Any]):
        if len(self.offline_queue) >= self.max_queue_size:
            # FIFO eviction of oldest items
            self.offline_queue.pop(0)
        self.offline_queue.append(payload)
        self._save_queue_to_disk()

    def flush_offline_queue(self):
        if not self.offline_queue:
            return

        print(f"[Agent Queue] Reconnected! Flushing {len(self.offline_queue)} offline telemetry records from disk...")
        to_flush = list(self.offline_queue)
        self.offline_queue.clear()
        self._save_queue_to_disk()

        for queued_item in to_flush:
            try:
                headers = dict(self.headers)
                token = queued_item.get("agent_token") or os.getenv("STUDIQ_AGENT_TOKEN", "")
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                res = requests.post(self.backend_url, json=queued_item, headers=headers, timeout=1.5)
                if res.status_code not in (200, 201):
                    self.offline_queue.append(queued_item)
            except Exception:
                self.offline_queue.append(queued_item)

        self._save_queue_to_disk()

    def send_popup_action(self, student_id: int, action: str) -> bool:
        """Sends popup response action to backend."""
        try:
            url = self.backend_url.replace("/monitoring/telemetry", "/monitoring/popup-action").replace("/monitoring/update", "/monitoring/popup-action")
            res = requests.post(url, json={"student_id": student_id, "action": action}, headers=self.headers, timeout=2.0)
            return res.status_code == 200
        except Exception:
            return False

    def send_heartbeat(self, student_id: int, student_code: str) -> bool:
        """Sends lightweight heartbeat to backend."""
        try:
            from datetime import datetime
            url = AgentConfig.HEARTBEAT_URL
            res = requests.post(
                url,
                json={
                    "student_id": student_id,
                    "student_code": student_code,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_version": "1.0.0"
                },
                headers=self.headers,
                timeout=1.5
            )
            return res.status_code == 200
        except Exception:
            return False

