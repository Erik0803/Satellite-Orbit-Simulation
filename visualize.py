from vpython import *
import numpy as np

# Constants
G = 6.67430e-11      # gravitational constant
M = 5.972e24         # mass of Earth (kg)
R = 6.371e6          # radius of Earth (m)

# Simulation parameters
altitude = 400e3     # 400 km above Earth
r = R + altitude
v = np.sqrt(G * M / r)
dt = 1               # time step (seconds)

# Create Earth
earth = sphere(pos=vector(0,0,0), radius=R, texture=textures.earth)

# Satellite object
satellite = sphere(pos=vector(r, 0, 0), radius=1e5, color=color.red, make_trail=True)
satellite.velocity = vector(0, v, 0)

# Display settings
scene.autoscale = False
scene.range = 1.5 * r

# Simulation loop
while True:
    rate(100)  # run at 100 steps/sec
    r_vec = satellite.pos - earth.pos
    r_mag = mag(r_vec)
    acc = -G * M / r_mag**3 * r_vec
    satellite.velocity += acc * dt
    satellite.pos += satellite.velocity * dt
