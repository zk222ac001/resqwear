import multiprocessing
import time
from simulator import run_simulator, build_devices

SCENARIOS = ["hiking", "skiing", "climbing", "sailing"]

class SimulatorManager:
    def __init__(self):
        self.processes = {}  # scenario -> Process

    def start_simulator(self, scenario: str, n_devices: int):
        if scenario in self.processes and self.processes[scenario].is_alive():
            print(f"[sim_manager] Simulator for '{scenario}' already running")
            return
        devices = build_devices(n=n_devices, scenario=scenario)
        p = multiprocessing.Process(target=run_simulator, args=(devices,), kwargs={"tick_seconds": 1.2})
        p.daemon = True
        p.start()
        self.processes[scenario] = p
        print(f"[sim_manager] Started simulator for '{scenario}' with {n_devices} devices")

    def stop_simulator(self, scenario: str):
        if scenario in self.processes:
            p = self.processes[scenario]
            if p.is_alive():
                p.terminate()
                p.join()
                print(f"[sim_manager] Stopped simulator '{scenario}'")
            del self.processes[scenario]

    def stop_all(self):
        for s in list(self.processes.keys()):
            self.stop_simulator(s)

    def status(self):
        return {s: (p.is_alive() if p else False) for s, p in self.processes.items()}

# Example usage
if __name__ == "__main__":
    mgr = SimulatorManager()
    mgr.start_simulator("hiking", 3)
    mgr.start_simulator("skiing", 2)
    time.sleep(5)
    print(mgr.status())
    mgr.stop_all()
