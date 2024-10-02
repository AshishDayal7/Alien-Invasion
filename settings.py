class Settings:
    # A class to store all settings for Alien Invasion.
    def __init__(self):
        # Initialize the game's settings.
        # Screen settings
        self.screen_width = 1100
        self.screen_height = 700
        self.bg_color = (0, 0, 0) #background color   
        self.ship_speed = 5.0
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed = 3.0
        self.bullet_width = 5
        self.bullet_height = 10
        self.bullet_color = (255, 255, 255)
        self.bullets_allowed = 7

        #alien settings
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10
        self.speedup_scale = 1.75
        self.score_scale = 1.5

        self.initialize_dynamic_settings()
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1


    def initialize_dynamic_settings(self):
        self.ship_speed = 5.0
        self.bullet_speed = 3.0
        self.alien_speed = 1.0
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        self.alien_points = 50

    def increase_speed(self):
        # Increase speed settings and alien point values.
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.fleet_drop_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
        print(self.alien_points)