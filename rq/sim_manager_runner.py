from sim_manager import SimulatorManager
from simulator import build_devices
import asyncio

# Start all default scenarios
mgr = SimulatorManager()
default_devices = 3

for scenario in ["hiking", "skiing", "climbing", "sailing"]:
    mgr.start_simulator(scenario, default_devices)

# Keep process alive
try:
    while True:
        asyncio.sleep(1) # type: ignore
except KeyboardInterrupt:
    mgr.stop_all()
