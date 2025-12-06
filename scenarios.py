import random
from dataclasses import dataclass
'''
This @dataclass automatically creates:
__init__
__repr__
field handling
The class describes a scenario (hiking, skiing, etc.) with:
name — text name of scenario.
base_speed_kph — average speed for the scenario.
speed_jitter — how much speed randomly varies.
temp_base — typical temperature.
temp_jitter — randomness added to temperature.
drift_m — how many meters the simulated person moves each “tick”.
'''
@dataclass
class ScenarioConfig:
    name: str
    base_speed_kph: float
    speed_jitter: float
    temp_base: float
    temp_jitter: float
    drift_m: float  # movement intensity (meters) per tick

'''
Hiking → slower movement, mild temp
Skiing → fast movement, cold, lots of drift
Climbing → slow movement, small drift
Sailing → medium speed, large drift
'''
SCENARIOS = {
    "hiking":   ScenarioConfig("hiking",   base_speed_kph=4.5,  speed_jitter=1.2, temp_base=12.0, temp_jitter=0.6, drift_m=55),
    "skiing":   ScenarioConfig("skiing",   base_speed_kph=18.0, speed_jitter=6.0, temp_base=-2.0, temp_jitter=0.9, drift_m=140),
    "climbing": ScenarioConfig("climbing", base_speed_kph=2.2,  speed_jitter=0.8, temp_base=8.0,  temp_jitter=0.5, drift_m=30),
    "sailing":  ScenarioConfig("sailing",  base_speed_kph=10.0, speed_jitter=3.5, temp_base=14.0, temp_jitter=0.7, drift_m=120),
}

'''
cfg → one of the scenarios above
lat, lon → current GPS coordinates
And returns:
new latitude
new longitude
simulated speed
simulated temperature
'''
def next_step(cfg: ScenarioConfig, lat: float, lon: float):
    # tiny “geo drift” (not geodesically perfect—good enough for simulation)
    def meters_to_deg(m: float):  # rough: ~111_000 m per degree latitude
        return m / 111_000.0

    speed = max(0.0, random.gauss(cfg.base_speed_kph, cfg.speed_jitter))
    drift = abs(random.gauss(cfg.drift_m, cfg.drift_m * 0.3))
    d = meters_to_deg(drift)
    lat += random.uniform(-d, d)
    lon += random.uniform(-d, d) / max(0.3, abs(lat) / 90 + 1e-6)  # crude lon scaling
    temp = random.gauss(cfg.temp_base, cfg.temp_jitter)
    return lat, lon, speed, temp
