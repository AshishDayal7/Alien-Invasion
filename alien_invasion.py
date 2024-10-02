import sys
from time import sleep
import pygame
from settings import Settings
from gamestats import GameStats
from score import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien



class AlienInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()                       #initialize background settings that Pygame needs to work properly
        self.clock = pygame.time.Clock()    #create an instance to track time
        self.settings = Settings()

        #create a display window for the game (can change later to automatic full screen)
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))  
        pygame.display.set_caption("Alien Invasion")
        
        self.stats = GameStats(self)            # Create an instance to store game statistics.
        self.sb = Scoreboard(self)              # Create a scoreboard.
        self.bg_color = (230, 230, 230)         #background color 
        self.ship = Ship(self)                  #create an instance of the ship after the screen has been created  
        self.bullets = pygame.sprite.Group()    #create a group to store the bullets
        self.aliens = pygame.sprite.Group()     #create a group to store the aliens
        self._create_fleet()
        self.game_active = False                #flag to indicate if the game is active

        self.play_button = Button(self, "Play")      #create a play button


    def run_game(self):
        """Start the main loop for the game."""
        # Redraw the screen during each pass through the loop.
       
        while True:
            self._check_events()    # respond to keypresses and mouse events
            if self.game_active:
                self.ship.update()      # update the ship's position
                self.update_bullets()   # update the bullets
                self._update_aliens()   # update the aliens
            self.update_screen()        # update the screen
            self.clock.tick(60)         # set the frame rate of the game to 60 frames per second

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)        
            elif event.type == pygame.KEYDOWN:          #respond to keypresses 
                self._check_keydown_events(event)
                
            elif event.type == pygame.KEYUP:            #respond to key releases
                self._check_keyup_events(event)

    #respond to keypresses
    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    
    #respond to key releases
    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)   

    def update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        self._check_bullet_alien_collisions()
            
       

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()
        


    def _create_fleet(self):
        # Create the fleet of aliens.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size

        current_x, current_y = alien_width, alien_height
        while current_y < (self.settings.screen_height - 5 *  alien_height):    
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2.5 *  alien_width
            # Reset the x position and move to the next row. and increment y value
            current_x = alien_width
            current_y += 2.5*  alien_height

    def _create_alien(self, x_position, y_position):
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        """Update the score."""
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 0:
            # Decrement ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()            # Update lifeline
            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            # Pause.
            sleep(0.5)
        else:
            self.game_active = False

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.settings.initialize_dynamic_settings()
            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            self.game_active = True
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()

    def update_screen(self):
        self.screen.fill(self.settings.bg_color) 
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()  
        self.ship.blitme() 
        self.aliens.draw(self.screen)
        self.sb.show_score()
        if not self.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible.
        pygame.display.flip()
             

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion() 
    ai.run_game() 