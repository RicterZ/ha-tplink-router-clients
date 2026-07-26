import hashlib
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location(
    "router_api",
    Path(__file__).parents[1] / "custom_components/tplink_router_clients/api.py",
)
router_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router_api)
RouterClient = router_api.RouterClient


class RouterClientTest(unittest.TestCase):
    def test_login_filters_and_sorts_online_clients(self):
        client = RouterClient("router.local", "admin", "secret")
        client._post = Mock(side_effect=[
            {"nonce": "nonce"},
            {"error_code": 0, "stok": "token"},
            {
                "error_code": 0,
                "host_management": {"host_info": [
                    {"host_1": {"state": "offline", "hostname": "old", "mac": "1", "ip": "0.0.0.0", "up_speed": "0", "down_speed": "0"}},
                    {"host_2": {"state": "online", "hostname": "slow", "mac": "2", "ip": "1.1.1.2", "up_speed": "1", "down_speed": "2"}},
                    {"host_3": {"state": "online", "hostname": "fast%20client", "mac": "3", "ip": "1.1.1.3", "up_speed": "3", "down_speed": "20"}}
                ]},
            },
        ])

        clients = client.online_clients()

        self.assertEqual([client["name"] for client in clients], ["fast client", "slow"])
        self.assertEqual(
            client._post.call_args_list[1].args[1]["login"]["password"],
            hashlib.md5(b"secret:nonce").hexdigest(),
        )
