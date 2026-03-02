"""
Operation Touchdown Simulator - ART IITK
Drone landing simulation with moving platform, camera feed, and configurable controller.
"""

import pygame
import math
import os
import sys

# --- CONSTANTS ---
PIXELS_PER_METER = 100
FPS = 30
SIM_TIME_SEC = 20  # Time until the drone touches the ground
LANDING_SUCCESS_M = 0.05  # STRICT: Distance from platform center to count as successful landing (5 cm)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (80, 80, 80)
BG_COLOR = (45, 90, 50)  # Grass-like background
PLATFORM_COLOR = (200, 200, 200)
DRONE_COLOR = (255, 50, 50)
TRAIL_COLOR = (255, 200, 100)
SUCCESS_COLOR = (80, 255, 120)
FAIL_COLOR = (255, 80, 80)


class DroneSim:
    def __init__(self, use_demo_controller=True):
        """
        Args:
            use_demo_controller: If True, use built-in Python controller (Demo mode).
                                 If False, read commands from commands.txt (For C/C++/External Python).
        """
        pygame.init()
        self.width, self.height = 1000, 800 # Widened the screen to give more search area
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("ART IITK - Operation Touchdown Simulator | ESC to quit")

        self.use_demo_controller = use_demo_controller
        self.time_elapsed = 0.0

        # --- LEVEL UP CHANGES ---
        
        # 1. Platform starts on the extreme RIGHT side
        self.plat_size = 1.0 * PIXELS_PER_METER
        self.start_x = self.width / 2 # 2.5 meters from the right edge
        self.plat_x = self.start_x / 2
        self.plat_y = self.height / 2
        
        # Platform Kinematics (Moves left and right by 1.5m)
        self.amplitude = 2.0 * PIXELS_PER_METER
        self.omega = 0.9

        # 2. Drone starts on the extreme LEFT side
        self.drone_x =  80

        self.drone_y = 180
        self.drone_altitude = 10.0

        # 3. Increase Simulation Time to allow for the "Search" phase
        global SIM_TIME_SEC
        SIM_TIME_SEC = 35 # Increased from 20 to 35 seconds
        self.drone_altitude = 10.0
        self.descent_rate = self.drone_altitude / SIM_TIME_SEC

        # 4. Restrict Camera FOV so the drone is BLIND to the platform at the start
        self.cam_resolution = 100
        # At 10m altitude, the drone will only see a 3m x 3m square on the ground.
        # Since it starts at x=1m and the platform is at x=7.5m, the camera feed will be purely grass!
        self.cam_ground_size_base = 0.30 
        self._last_cam_surface = None

        # Trajectory trail
        self.trail = []
        self.trail_max_len = 120

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("consolas", 20, bold=True)
        self.big_font = pygame.font.SysFont("consolas", 48, bold=True)
    # def __init__(self, use_demo_controller=True):
    #     """
    #     Args:
    #         use_demo_controller: If True, use built-in Python controller (Demo mode).
    #                              If False, read commands from commands.txt (For C/C++/External Python).
    #     """
    #     pygame.init()
    #     self.width, self.height = 800, 800
    #     self.screen = pygame.display.set_mode((self.width, self.height))
    #     pygame.display.set_caption("ART IITK - Operation Touchdown Simulator | ESC to quit")

    #     self.use_demo_controller = use_demo_controller
    #     self.time_elapsed = 0.0

    #     # Platform variables
    #     self.plat_size = 1.0 * PIXELS_PER_METER
    #     self.start_x = self.width / 2
    #     self.plat_x = self.start_x
    #     self.plat_y = self.height / 2
        
    #     # Kinematics for Platform (Simple Harmonic Motion for smooth acceleration)
    #     # x(t) = A * sin(w * t) -> v(t) = A * w * cos(w * t)
    #     # Max velocity = A * w. We want max v = 0.5 m/s. 
    #     # We want max amplitude A = 1.0 m. Therefore w = 0.5.
    #     self.amplitude = 2.0 * PIXELS_PER_METER
    #     self.omega = 0.7

    #     # Drone
    #     self.drone_x = self.width / 2 + 150
    #     self.drone_y = self.height / 2 - 100
    #     self.drone_altitude = 10.0
    #     self.descent_rate = self.drone_altitude / SIM_TIME_SEC

    #     # Camera: ground area seen scales with altitude (perspective)
    #     self.cam_resolution = 100
    #     self.cam_ground_size_base = 2.5  # meters at altitude 1.0
    #     self._last_cam_surface = None

    #     # Trajectory trail
    #     self.trail = []
    #     self.trail_max_len = 120

    #     self.clock = pygame.time.Clock()
    #     self.font = pygame.font.SysFont("consolas", 20, bold=True)
    #     self.big_font = pygame.font.SysFont("consolas", 48, bold=True)

    def _ground_size_at_altitude(self):
        """Ground area (meters) visible in camera scales with altitude."""
        return self.cam_ground_size_base * max(0.1, self.drone_altitude)

    def update_platform(self, dt):
        """Updates platform position using SHM for smooth acceleration/deceleration"""
        self.time_elapsed += dt
        offset = self.amplitude * math.sin(self.omega * self.time_elapsed)
        self.plat_x = self.start_x + offset

    def generate_camera_feed(self):
        """Generate down-facing camera image. FOV scales with altitude."""
        ground_m = self._ground_size_at_altitude()
        ground_px = ground_m * PIXELS_PER_METER
        cam_size = int(min(800, max(100, ground_px)))

        cam_surface = pygame.Surface((cam_size, cam_size))
        cam_surface.fill(BG_COLOR)

        # Platform position in world; offset for drone center
        rel_x = self.plat_x - (self.drone_x - cam_size / 2)
        rel_y = self.plat_y - (self.drone_y - cam_size / 2)

        rect = pygame.Rect(
            rel_x - self.plat_size / 2, rel_y - self.plat_size / 2,
            self.plat_size, self.plat_size
        )
        pygame.draw.rect(cam_surface, PLATFORM_COLOR, rect)
        inner = pygame.Rect(
            rel_x - self.plat_size / 4, rel_y - self.plat_size / 4,
            self.plat_size / 2, self.plat_size / 2
        )
        pygame.draw.rect(cam_surface, BLACK, inner)

        # Downsample to 100x100 for student code compatibility
        scaled = pygame.transform.scale(cam_surface, (self.cam_resolution, self.cam_resolution))
        self._last_cam_surface = scaled

        try:
            with open("camera_pixels.txt", "w") as f:
                for y in range(self.cam_resolution):
                    for x in range(self.cam_resolution):
                        r, g, b, a = scaled.get_at((x, y))
                        gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                        f.write(f"{gray} ")
                    f.write("\n")
        except IOError:
            pass # Ignore read/write collisions

    def demo_controller(self):
        """Simple proportional controller: steer toward platform center."""
        vx = 0.0
        vy = 0.0
        return vx, vy

    def read_commands(self):
        vx, vy = 0.0, 0.0
        try:
            if os.path.exists("commands.txt"):
                with open("commands.txt", "r") as f:
                    data = f.read().strip().split()
                    if len(data) >= 2:
                        vx, vy = float(data[0]), float(data[1])
        except Exception:
            pass
        return vx, vy

    def get_commands(self):
        if self.use_demo_controller:
            return self.demo_controller()
        return self.read_commands()

    def run(self):
        running = True
        while running and self.drone_altitude > 0:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            # Physics
            self.update_platform(dt)
            self.drone_altitude -= self.descent_rate * dt

            self.generate_camera_feed()
            vx, vy = self.get_commands()
            self.drone_x += vx * PIXELS_PER_METER * dt
            self.drone_y += vy * PIXELS_PER_METER * dt

            # Trail
            self.trail.append((self.drone_x, self.drone_y))
            if len(self.trail) > self.trail_max_len:
                self.trail.pop(0)

            # Render
            self._render()
            pygame.display.flip()

        # Result Evaluation
        final_error = math.hypot(
            self.drone_x - self.plat_x,
            self.drone_y - self.plat_y
        ) / PIXELS_PER_METER
        success = final_error <= LANDING_SUCCESS_M
        print(f"TOUCHDOWN! Final distance: {final_error:.3f} m — {'SUCCESS' if success else 'FAILED'}")

        self._render_result(success, final_error)
        pygame.display.flip()

        # Wait for key or delay
        pygame.time.wait(2500)
        for _ in range(90):
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    pygame.quit()
                    return
            pygame.time.wait(50)

        pygame.quit()

    def _draw_grid(self):
        step = PIXELS_PER_METER // 2
        for x in range(0, self.width + 1, step):
            c = DARK_GRAY if x % PIXELS_PER_METER else GRAY
            pygame.draw.line(self.screen, c, (x, 0), (x, self.height), 1)
        for y in range(0, self.height + 1, step):
            c = DARK_GRAY if y % PIXELS_PER_METER else GRAY
            pygame.draw.line(self.screen, c, (0, y), (self.width, y), 1)

    def _draw_drone(self):
        """Draws a 3D-looking quadcopter with an altitude-based shadow"""
        # Shadow (gets smaller and darker as altitude drops)
        shadow_offset = self.drone_altitude * 3
        shadow_radius = max(10, int(40 - self.drone_altitude * 2))
        shadow_alpha = max(50, int(200 - self.drone_altitude * 10))
        shadow_surface = pygame.Surface((150, 150), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, shadow_alpha), (75 + shadow_offset, 75 + shadow_offset), shadow_radius)
        self.screen.blit(shadow_surface, (self.drone_x - 75, self.drone_y - 75))

        # Drone Body Frame
        arm_len = 35
        pygame.draw.line(self.screen, WHITE, (self.drone_x - arm_len, self.drone_y - arm_len), (self.drone_x + arm_len, self.drone_y + arm_len), 4)
        pygame.draw.line(self.screen, WHITE, (self.drone_x - arm_len, self.drone_y + arm_len), (self.drone_x + arm_len, self.drone_y - arm_len), 4)
        pygame.draw.circle(self.screen, DRONE_COLOR, (int(self.drone_x), int(self.drone_y)), 10)

        # Spinning Rotors
        rotor_radius = 16
        rotor_offset = int(math.sin(self.time_elapsed * 25) * 3) # Simulate fast blur
        for dx, dy in [(-1, -1), (1, 1), (-1, 1), (1, -1)]:
            rx = self.drone_x + dx * arm_len
            ry = self.drone_y + dy * arm_len
            pygame.draw.circle(self.screen, DARK_GRAY, (int(rx), int(ry)), rotor_radius + rotor_offset, 2)

        # Field of View Indicator
        ground_m = self._ground_size_at_altitude()
        view_r = int(ground_m * PIXELS_PER_METER / 2)
        pygame.draw.circle(self.screen, DRONE_COLOR, (int(self.drone_x), int(self.drone_y)), view_r, 1)

    def _render(self):
        self.screen.fill(BG_COLOR)
        self._draw_grid()

        # Trail
        if len(self.trail) >= 2:
            pts = [(int(x), int(y)) for x, y in self.trail]
            pygame.draw.lines(self.screen, TRAIL_COLOR, False, pts, 2)

        # Platform
        plat_rect = pygame.Rect(
            self.plat_x - self.plat_size / 2, self.plat_y - self.plat_size / 2,
            self.plat_size, self.plat_size
        )
        pygame.draw.rect(self.screen, PLATFORM_COLOR, plat_rect, 0)
        pygame.draw.rect(self.screen, WHITE, plat_rect, 2)
        inner = pygame.Rect(
            self.plat_x - self.plat_size / 4, self.plat_y - self.plat_size / 4,
            self.plat_size / 2, self.plat_size / 2
        )
        pygame.draw.rect(self.screen, BLACK, inner)

        # Success zone (faint)
        success_r = int(LANDING_SUCCESS_M * PIXELS_PER_METER)
        s = pygame.Surface((success_r * 2, success_r * 2))
        s.set_alpha(60)
        s.fill(SUCCESS_COLOR)
        self.screen.blit(s, (self.plat_x - success_r, self.plat_y - success_r))
        pygame.draw.circle(self.screen, SUCCESS_COLOR, (int(self.plat_x), int(self.plat_y)), success_r, 1)

        # Drone
        self._draw_drone()

        # UI Panel
        ui_rect = pygame.Rect(10, 10, 250, 90)
        pygame.draw.rect(self.screen, (20, 20, 20, 220), ui_rect, border_radius=8)
        
        alt_text = self.font.render(f"Altitude: {self.drone_altitude:.2f} m", True, WHITE)
        err = math.hypot(self.drone_x - self.plat_x, self.drone_y - self.plat_y) / PIXELS_PER_METER
        
        # Color code the error text dynamically
        err_color = SUCCESS_COLOR if err <= LANDING_SUCCESS_M else FAIL_COLOR
        err_text = self.font.render(f"Error:    {err:.3f} m", True, err_color)
        
        ctrl_text = self.font.render("Mode: Demo" if self.use_demo_controller else "Mode: Ext. C/C++ Code", True, GRAY)
        self.screen.blit(alt_text, (20, 15))
        self.screen.blit(err_text, (20, 40))
        self.screen.blit(ctrl_text, (20, 65))

        # Camera preview
        if self._last_cam_surface:
            prev_bg = pygame.Rect(self.width - 120, 10, 110, 130)
            pygame.draw.rect(self.screen, (20, 20, 20, 220), prev_bg, border_radius=8)
            
            prev_rect = pygame.Rect(self.width - 115, 15, 100, 100)
            pygame.draw.rect(self.screen, BLACK, prev_rect)
            pygame.draw.rect(self.screen, WHITE, prev_rect, 1)
            
            scaled = pygame.transform.scale(self._last_cam_surface, (100, 100))
            self.screen.blit(scaled, (self.width - 115, 15))
            
            cam_label = self.font.render("CAM FEED", True, GRAY)
            self.screen.blit(cam_label, (self.width - 105, 120))

    def _render_result(self, success, final_error):
        self._render()
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        color = SUCCESS_COLOR if success else FAIL_COLOR
        msg = "LANDING SUCCESS!" if success else "LANDING FAILED"
        text = self.big_font.render(msg, True, color)
        rect = text.get_rect(center=(self.width / 2, self.height / 2 - 40))
        self.screen.blit(text, rect)

        sub = self.font.render(f"Final Offset: {final_error:.3f} meters", True, WHITE)
        sub_rect = sub.get_rect(center=(self.width / 2, self.height / 2 + 15))
        self.screen.blit(sub, sub_rect)
        
        req = self.font.render(f"Requirement: <= {LANDING_SUCCESS_M} m", True, GRAY)
        req_rect = req.get_rect(center=(self.width / 2, self.height / 2 + 45))
        self.screen.blit(req, req_rect)


if __name__ == "__main__":
    # If a user runs `python simulator.py --c`, it will disable the internal demo controller 
    # and wait for an external script (C, C++, or Python) to write to commands.txt
    use_demo = "--c" not in sys.argv
    sim = DroneSim(use_demo_controller=use_demo)
    
    if use_demo:
        print("Running in DEMO mode. Use 'python simulator.py --c' to read from commands.txt instead.")
    else:
        print("Running in EXTERNAL mode. Waiting for C/C++/Python code to write to commands.txt...")
        
    sim.run()