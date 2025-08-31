from vpython import *

class SatelliteSimulation:
    """Satellite orbital mechanics simulation using VPython"""
    
    # Physical constants
    G = 6.67430e-11  # Gravitational constant
    EARTH_MASS = 5.972e24  # kg
    EARTH_RADIUS = 6.371e6  # m
    
    # Simulation parameters
    DEFAULT_ALTITUDE = 700e3  # 700 km
    DEFAULT_SPEED = 7508.0  # m/s
    SIMULATION_RATE = 100  # Hz
    TIME_STEP = 1  # seconds
    
    # Visual parameters
    SATELLITE_RADIUS = 1e5
    VELOCITY_ARROW_SCALE = 3e6
    ARROW_WIDTH = 5e4
    
    def __init__(self):
        self.running = False
        self.initial_position = vector(self.EARTH_RADIUS + self.DEFAULT_ALTITUDE, 0, 0)
        self.setup_scene()
        self.create_objects()
        self.create_ui()
        self.reset_simulation()
    
    def setup_scene(self):
        """Initialize the 3D scene"""
        scene.title = "Satellite Orbit Simulation"
        scene.background = color.black
        scene.width = 1200
        scene.height = 800
        scene.range = 2.5 * mag(self.initial_position)
        scene.forward = vector(-1, -1, -1)
        scene.up = vector(0, 0, 1)
    
    def create_objects(self):
        """Create 3D objects for visualization"""
        # Earth
        self.earth = sphere(
            pos=vector(0, 0, 0),
            radius=self.EARTH_RADIUS,
            texture=textures.earth
        )
        
        # Satellite
        self.satellite = sphere(
            pos=self.initial_position,
            radius=self.SATELLITE_RADIUS,
            color=color.red,
            make_trail=True,
            trail_type="points",
            interval=10,
            retain=500
        )
        
        # Velocity vector arrow
        self.velocity_arrow = arrow(
            pos=self.satellite.pos,
            axis=vector(0, self.DEFAULT_SPEED, 0).norm() * self.VELOCITY_ARROW_SCALE,
            color=color.cyan,
            shaftwidth=self.ARROW_WIDTH
        )
        
        # Labels
        self.velocity_label = label(
            pos=self.velocity_arrow.pos + self.velocity_arrow.axis * 1.2,
            text='',
            height=16,
            border=4,
            font='monospace',
            box=True,
            color=color.cyan,
            background=color.black
        )
        
        self.info_label = label(
            pos=vector(0, self.EARTH_RADIUS * 1.8, 0),
            text="Set initial velocity components and launch satellite",
            height=20,
            box=False,
            color=color.white
        )
        
        self.status_label = label(
            pos=vector(0, -self.EARTH_RADIUS * 1.8, 0),
            text="Ready to launch",
            height=16,
            box=False,
            color=color.yellow
        )
    
    def create_ui(self):
        """Create user interface elements"""
        # Velocity input section
        wtext(text="<b>Initial Velocity Components (m/s):</b>\n")
        
        wtext(text="X: ")
        self.vx_input = winput(text="0", width=100, bind=self.update_velocity_vector)
        
        wtext(text="  Y: ")
        self.vy_input = winput(text=str(self.DEFAULT_SPEED), width=100, bind=self.update_velocity_vector)
        
        wtext(text="  Z: ")
        self.vz_input = winput(text="0", width=100, bind=self.update_velocity_vector)
        
        wtext(text="\n\n")
        
        # Control buttons
        self.launch_button = button(text="🚀 Launch Satellite", bind=self.launch_satellite)
        wtext(text="  ")
        self.reset_button = button(text="🔄 Reset", bind=self.reset_simulation)
        
        wtext(text="\n\n<b>Orbital Parameters:</b>\n")
        self.orbital_info = wtext(text="")
        
    def get_velocity_from_inputs(self):
        """Parse velocity inputs and return vector"""
        try:
            vx = float(self.vx_input.text)
            vy = float(self.vy_input.text)
            vz = float(self.vz_input.text)
            return vector(vx, vy, vz)
        except ValueError:
            return None
    
    def update_velocity_vector(self, event=None):
        """Update velocity arrow and label based on input"""
        velocity = self.get_velocity_from_inputs()
        if velocity is None:
            return
            
        self.satellite.velocity = velocity
        
        # Update arrow
        if mag(velocity) > 0:
            self.velocity_arrow.axis = velocity.norm() * self.VELOCITY_ARROW_SCALE
        else:
            self.velocity_arrow.axis = vector(0, 0, 0)
        
        self.velocity_arrow.pos = self.satellite.pos
        
        # Update label
        self.velocity_label.pos = self.velocity_arrow.pos + self.velocity_arrow.axis * 1.2
        self.velocity_label.text = (
            f"V = ({velocity.x:.1f}, {velocity.y:.1f}, {velocity.z:.1f}) m/s\n"
            f"|V| = {mag(velocity):.1f} m/s"
        )
        
        # Calculate orbital parameters
        self.update_orbital_info(velocity)
    
    def update_orbital_info(self, velocity):
        """Calculate and display orbital parameters"""
        r = mag(self.satellite.pos)
        v = mag(velocity)
        
        # Specific orbital energy
        energy = 0.5 * v**2 - self.G * self.EARTH_MASS / r
        
        # Circular orbital velocity at current altitude
        v_circular = sqrt(self.G * self.EARTH_MASS / r)
        
        # Escape velocity at current altitude
        v_escape = sqrt(2 * self.G * self.EARTH_MASS / r)
        
        # Determine orbit type
        if energy < 0:
            orbit_type = "Elliptical"
        elif energy == 0:
            orbit_type = "Parabolic (Escape)"
        else:
            orbit_type = "Hyperbolic (Escape)"
        
        altitude = (r - self.EARTH_RADIUS) / 1000  # km
        
        info_text = (
            f"Altitude: {altitude:.1f} km\n"
            f"Current speed: {v:.1f} m/s\n"
            f"Circular speed: {v_circular:.1f} m/s\n"
            f"Escape speed: {v_escape:.1f} m/s\n"
            f"Orbit type: {orbit_type}\n"
            f"Specific energy: {energy:.0f} J/kg"
        )
        
        self.orbital_info.text = info_text
    
    def launch_satellite(self, event=None):
        """Start the orbital simulation"""
        if self.running:
            return
            
        velocity = self.get_velocity_from_inputs()
        if velocity is None:
            return
            
        self.running = True
        self.satellite.velocity = velocity
        
        # Hide UI elements during simulation
        self.velocity_arrow.visible = False
        self.velocity_label.visible = False
        self.info_label.visible = False
        
        self.status_label.text = "Simulation running..."
        self.status_label.color = color.green
        
        self.launch_button.disabled = True
        self.reset_button.disabled = False
    
    def reset_simulation(self, event=None):
        """Reset simulation to initial state"""
        self.running = False
        
        # Reset satellite
        self.satellite.pos = self.initial_position
        self.satellite.velocity = vector(0, self.DEFAULT_SPEED, 0)
        self.satellite.clear_trail()
        self.satellite.visible = True
        
        # Show UI elements
        self.velocity_arrow.visible = True
        self.velocity_label.visible = True
        self.info_label.visible = True
        
        # Reset inputs
        self.vx_input.text = "0"
        self.vy_input.text = str(self.DEFAULT_SPEED)
        self.vz_input.text = "0"
        
        self.update_velocity_vector()
        
        # Reset buttons
        self.launch_button.disabled = False
        self.reset_button.disabled = True
        
        self.status_label.text = "Ready to launch"
        self.status_label.color = color.yellow
    
    def create_explosion(self, position):
        """Create explosion animation when satellite crashes"""
        explosion = sphere(
            pos=position,
            radius=self.SATELLITE_RADIUS,
            color=color.orange,
            emissive=True
        )
        
        # Animate explosion
        for _ in range(30):
            rate(60)
            explosion.radius += 4e4
            explosion.opacity = max(0, explosion.opacity - 0.033)
        
        explosion.visible = False
    
    def check_collision(self):
        """Check if satellite has collided with Earth"""
        distance = mag(self.satellite.pos - self.earth.pos)
        return distance <= self.EARTH_RADIUS
    
    def update_physics(self):
        """Update satellite position using gravitational physics"""
        # Calculate gravitational force
        r_vector = self.satellite.pos - self.earth.pos
        r_magnitude = mag(r_vector)
        
        # Gravitational acceleration
        acceleration = -self.G * self.EARTH_MASS / r_magnitude**3 * r_vector
        
        # Update velocity and position (Euler integration)
        self.satellite.velocity += acceleration * self.TIME_STEP
        self.satellite.pos += self.satellite.velocity * self.TIME_STEP
        
        # Update status
        altitude = (r_magnitude - self.EARTH_RADIUS) / 1000
        speed = mag(self.satellite.velocity)
        self.status_label.text = f"Altitude: {altitude:.1f} km | Speed: {speed:.1f} m/s"
    
    def run(self):
        """Main simulation loop"""
        while True:
            rate(self.SIMULATION_RATE)
            
            if not self.running:
                continue
            
            # Check for collision
            if self.check_collision():
                self.create_explosion(self.satellite.pos)
                self.satellite.visible = False
                self.running = False
                self.launch_button.disabled = True
                self.reset_button.disabled = False
                self.status_label.text = "Satellite crashed! Press Reset to try again."
                self.status_label.color = color.red
                continue
            
            # Update physics
            self.update_physics()

# Create and run simulation
if __name__ == "__main__":
    sim = SatelliteSimulation()
    sim.run()