import asyncio
import json
import os
import random
import uuid
import websockets
import argparse
from datetime import datetime, timezone
from db import DB
from models import Transport, EventType, AlertType
from scenarios import SCENARIOS, next_step

HOST = "127.0.0.1"
PORT = int(os.environ.get("RESQWEAR_SIM_PORT", "8765"))

class SimDevice:
    def __init__(self, device_id, name, scenario, lat, lon):
        self.device_id = device_id
        self.name = name
        self.scenario = scenario
        self.lat = lat
        self.lon = lon
        self.last_ts = datetime.now(timezone.utc)

async def run_simulator(devices, tick_seconds=1.2, transport_mix=("udp", "tcp")):
    db = DB()
    await db.init()

    async def broadcast(ws_clients, payload: dict):
        if not ws_clients:
            return
        msg = json.dumps(payload)
        await asyncio.gather(*[c.send(msg) for c in ws_clients if not c.closed], return_exceptions=True)

    ws_clients = set()

    async def ws_handler(websocket):
        ws_clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            ws_clients.discard(websocket)

    server = await websockets.serve(ws_handler, HOST, PORT)
    print(f"[sim] websocket server up on ws://{HOST}:{PORT}")

    while True:
        for d in devices:
            cfg = SCENARIOS[d.scenario]
            d.lat, d.lon, speed, temp = next_step(cfg, d.lat, d.lon)

            ts = datetime.now(timezone.utc)

            # heartbeat / status
            await db.upsert_device(d.device_id, d.name, d.scenario, "online", ts)

            # location event
            loc_evt = {
                "type": EventType.LOCATION,
                "transport": random.choice(transport_mix),
                "device_id": d.device_id,
                "ts": ts.isoformat(),
                "payload": {"lat": d.lat, "lon": d.lon, "speed_kph": speed},
            }
            await db.insert_position(d.device_id, ts, d.lat, d.lon, speed, loc_evt["transport"])
            await broadcast(ws_clients, loc_evt)

            # temperature event
            temp_evt = {
                "type": EventType.TEMPERATURE,
                "transport": random.choice(transport_mix),
                "device_id": d.device_id,
                "ts": ts.isoformat(),
                "payload": {"temp_c": temp},
            }
            await db.insert_temp(d.device_id, ts, temp, temp_evt["transport"])
            await broadcast(ws_clients, temp_evt)

            # occasional spontaneous “SOS” (rare) to show alert pipeline
            if random.random() < 0.02:  # 2% chance per tick per device
                alert_id = str(uuid.uuid4())
                alert = {
                    "type": EventType.ALERT,
                    "transport": random.choice(transport_mix),
                    "device_id": d.device_id,
                    "ts": ts.isoformat(),
                    "payload": {
                        "alert_id": alert_id,
                        "alert_type": AlertType.SOS,
                        "severity": 5,
                        "message": f"Automatic SOS (simulated) for {d.name}",
                    },
                }
                await db.upsert_alert(
                    alert_id, d.device_id, str(AlertType.SOS), alert["payload"]["message"], 5, ts, resolved=False
                )
                await broadcast(ws_clients, alert)

        await asyncio.sleep(tick_seconds)

def build_devices(n=3, scenario="hiking", center=(55.6761, 12.5683)):
    devices=[]
    base_lat, base_lon = center
    for i in range(1, n+1):
        dev_id = f"RQ-{1000+i}"
        name = f"ResQWear {i}"
        # small offset so markers are visible
        lat = base_lat + (i * 0.002)
        lon = base_lon + (i * 0.0025)
        devices.append(SimDevice(dev_id, name, scenario, lat, lon))
    return devices

if __name__ == "__main__":   
    p = argparse.ArgumentParser()
    p.add_argument("--devices", type=int, default=3)
    p.add_argument("--scenario", type=str, default="hiking", choices=list(SCENARIOS.keys()))
    p.add_argument("--tick", type=float, default=1.2)
    args = p.parse_args()
    asyncio.run(run_simulator(build_devices(args.devices, args.scenario), tick_seconds=args.tick))
