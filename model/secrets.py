import json
from pathlib import Path

from cryptography.fernet import Fernet


class EncryptedSecrets:
    sensitive_keys = ["api_key", "password", "token"]

    def __init__(
        self, directory: Path, filename: str = "secrets.json", keyfile: str = "secret.key"
    ):
        self.directory = Path(directory)
        self.path = self.directory / filename
        self.key_path = self.directory / keyfile

        self.directory.mkdir(parents=True, exist_ok=True)
        self._ensure_key()
        self._ensure_secrets_file()

        self.fernet = Fernet(self._load_key())

    def _ensure_key(self):
        if not self.key_path.exists():
            key = Fernet.generate_key()
            self.key_path.write_bytes(key)

    def _ensure_secrets_file(self):
        if not self.path.exists():
            self.path.write_text(json.dumps({}, indent=2))

    def _load_key(self) -> bytes:
        return self.key_path.read_bytes()

    def load(self) -> dict:
        data = json.loads(self.path.read_text())
        for k in (k for k in self.sensitive_keys if k in data):
            data[k] = self.fernet.decrypt(data[k].encode()).decode()
        return data

    def save(self, data: dict):
        encrypted = data.copy()
        for k in (k for k in self.sensitive_keys if k in encrypted):
            encrypted[k] = self.fernet.encrypt(encrypted[k].encode()).decode()
        self.path.write_text(json.dumps(encrypted, indent=2))
