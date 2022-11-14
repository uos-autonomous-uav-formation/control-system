# Introduction

All the functions that make the public API have their respective docstring with more detailed information on how it works. This is just a simple quick start guide

# Interacting with the flight simulator

Create the simulator object to connect to the flight sim to send and recieve data
```python
from src.flightsim import Simulator, DREFs
sim = Simulator()
```

Request DREFs to be sent at a specific frequency
```python
sim.add_freq_value(DREFs.lat, 60)
sim.add_freq_value(DREFs.long, 60)
```

Call the update method to recieve the latest data from X-Plane at least once a cycle
```python
sim.update()
print(sim.get(DREFs.lat), sim.get(DREFs.long))
```

Set a DREF using and passing the value
```python
sim.set(DREFs.side_force, 1000)
```

## X-Plane data
All X-Plane data references can be found in 
https://developer.x-plane.com/datarefs/
although the documentation is not perfect and some tinkering is required

### Using the DREFs class

The DREFs class found in flightsim.DREFs can be used to make using DREFs more readable, follow same structure.

#### Using multiplayer DREFs
A single multiplayer DREF can be used with up to 19 aircraft but each DREF may be formated in a different way, for this reason, multiplayer DREFs must be set up such that they are used using the format method passing a single id for the aircraft

```python
DREFs.multiplayer.opengl_roll.format(acft_id)
```

# Generating a leader

Generating a leader is very basic, for a cone shape use (the min_distance, max_distance and angle are optional, see dosctring for more information)

```python
from src.flightsim import *

sim = Simulator()

a = cone_leadergen(sim, 1, min_distance=10, max_distance=100, angle=10).load_leader()
a.join()
```

The function load_leader() returns a thread which, if the main thread finishes at some point, needs to be joined then.
