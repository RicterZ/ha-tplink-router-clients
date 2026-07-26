import hashlib
import json
import ssl
from urllib.parse import unquote
from urllib.request import Request, urlopen

TLS = ssl._create_unverified_context()


class RouterError(Exception):
    pass


class RouterClient:
    def __init__(self, host, username, password):
        self.base_url = f"https://{host.removeprefix('https://').rstrip('/')}"
        self.username = username
        self.password = password
        self.token = None

    def _post(self, path, data):
        request = Request(
            self.base_url + path,
            json.dumps(data).encode(),
            {"Content-Type": "application/json"},
        )
        try:
            with urlopen(request, timeout=5, context=TLS) as response:
                return json.load(response)
        except (OSError, ValueError) as error:
            raise RouterError(str(error)) from error

    def login(self):
        info = self._post(
            "/", {"method": "do", "user_management": {"get_encrypt_info": None}}
        )
        password = hashlib.md5(
            f"{self.password}:{info['nonce']}".encode()
        ).hexdigest()
        result = self._post("/", {"method": "do", "login": {
            "username": self.username,
            "password": password,
            "encrypt_type": "3",
        }})
        if result.get("error_code") != 0:
            raise RouterError("Login failed")
        self.token = result["stok"]

    def online_clients(self):
        if not self.token:
            self.login()
        try:
            return self._fetch_clients()
        except RouterError:
            self.token = None
            self.login()
            return self._fetch_clients()

    def _fetch_clients(self):
        result = self._post(f"/stok={self.token}/ds", {
            "method": "get",
            "host_management": {
                "table": "host_info",
                "para": {"start": 0, "end": 999},
            },
        })
        if result.get("error_code") != 0:
            raise RouterError("Failed to fetch clients")

        clients = []
        for item in result["host_management"]["host_info"]:
            host = next(iter(item.values()))
            if host["state"] == "online":
                clients.append({
                    "name": unquote(host["hostname"]),
                    "mac": host["mac"],
                    "ip": host["ip"],
                    "up": int(host["up_speed"] or 0),
                    "down": int(host["down_speed"] or 0),
                })
        return sorted(clients, key=lambda client: client["down"], reverse=True)

