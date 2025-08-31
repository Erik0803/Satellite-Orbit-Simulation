from vpython import *
import numpy as np

# Constants
G = 6.67430e-11
M = 5.972e24         # Earth mass (kg)
R = 6.371e6          # Earth radius (m)

# Initial position of satellite
init_pos = vector(R + 700e3, 0, 0)  # 700 km altitude

# Setup scene
scene.title = "Interactive Satellite Orbit Simulation"
scene.background = color.black
scene.width = 1000
scene.height = 700
scene.range = 2 * mag(init_pos)
scene.forward = vector(-1, -1, -1)

# Earth
earth = sphere(pos=vector(0, 0, 0), radius=R, texture=textures.earth)

# Satellite
satellite = sphere(pos=init_pos, radius=1e5, color=color.red, make_trail=True)
satellite.velocity = vector(0, 7300, 0)  # default velocity

# Velocity vector arrow
v_arrow = arrow(pos=satellite.pos, axis=satellite.velocity.norm() * 3e6, color=color.cyan, shaftwidth=5e4)

# Drag control
dragging = False

def drag_velocity(evt):
    global dragging
    dragging = True
    while dragging:
        rate(60)
        # Update arrow axis while dragging
        v_arrow.axis = scene.mouse.project(normal=vector(0, 0, 1)) - v_arrow.pos if scene.mouse.project(normal=vector(0, 0, 1)) else v_arrow.axis

def drop_velocity(evt):
    global dragging
    dragging = False

v_arrow.visible = True
v_arrow.headwidth = 1e5
v_arrow.headlength = 2e5
v_arrow.pickable = True

# Bind mouse events to drag velocity vector
scene.bind("mousedown", drag_velocity)
scene.bind("mouseup", drop_velocity)

# Wait for user to set vector
label(pos=vector(0, R*1.2, 0), text="Drag the cyan arrow to set velocity vector,\nthen click anywhere to start simulation", height=30, box=False)

# Wait for click
scene.waitfor("click")
satellite.velocity = v_arrow.axis.norm() * satellite.velocity.mag  # Set direction, keep speed magnitude
v_arrow.visible = False

# Simulation settings
dt = 1
running = True

# Explosion function
def explode(pos):
    explosion = sphere(pos=pos, radius=1e5, color=color.orange, emissive=True)
    for i in range(20):
        rate(50)
        explosion.radius += 5e4
        explosion.opacity -= 0.05
    explosion.visible = False

# Main simulation loop
while running:
    rate(100)
    r_vec = satellite.pos - earth.pos
    r_mag = mag(r_vec)

    # Collision detection
    if r_mag <= R:
        explode(satellite.pos)
        satellite.visible = False
        running = False
        break

    # Physics
    acc = -G * M / r_mag**3 * r_vec
    satellite.velocity += acc * dt
    satellite.pos += satellite.velocity * dt
