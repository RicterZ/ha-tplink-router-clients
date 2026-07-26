# TP-Link Router Clients

A Home Assistant custom integration that displays online TP-Link router clients, sorted by download speed.

> [!WARNING]
> TLS certificate verification is disabled because the target router setup does not provide a certificate chain trusted by Python. Use this integration only with a router you trust.

## Quick start

1. Copy `custom_components/tplink_router_clients` into Home Assistant's `custom_components` directory.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration** and select **TP-Link Router Clients**.
4. Enter the router host or IP, username, password, update interval, card layout, and displayed columns.

The setup validates the login before saving. Later changes to the update interval or card display are available under **Configure** on the integration.

## Add the dashboard card

The integration loads the bundled card automatically. Add a manual card:

```yaml
type: custom:tplink-router-clients-card
entity: sensor.tp_link_router_clients_online_clients
```

If Home Assistant generated a different entity ID, select the integration's **Online clients** sensor and use that ID instead.

## Configuration

| Setting | Default | Description |
| --- | --- | --- |
| Host or IP | — | Router hostname or IP address; HTTPS is used automatically. |
| Username | `admin` | Router administrator username. |
| Password | — | Router administrator password. |
| Update interval | 5 seconds | Polling interval from 2 to 300 seconds. |
| Card layout | `table` | `table` or `compact`. |
| Displayed columns | All | Device, MAC, IP, upload speed, and download speed. |

The integration creates one sensor. Its state is the number of online clients; the sorted client list is stored in the `clients` attribute for the bundled card.

## Test

The API parser and login flow use only the Python standard library:

```bash
python3 -m unittest discover -s tests -v
```

This integration currently targets the TP-Link API used by TL-R5009PE-AC firmware `1.0.30 Build 20260108 Rel.79937`.
