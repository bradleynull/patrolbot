import pygame
from pygame.locals import *
import os
from time import sleep
import RPi.GPIO as GPIO


class PiTftMainWindow:
    """Class to stand up the main GUI window and user controls on the PiTFT
    display"""

    TOUCH_UP = "UP"
    """The string that represents the up state for the touch screen."""
    TOUCH_DOWN = "DOWN"
    """The string that represents the down state for the touch screen."""

    def __init__(self, window_size):
        """Constructor

        Args:
            window_size((int, int)): The resolution to make the window.
        """

        # The constant size of this window
        self.size = window_size

        # The current state of the touch screen (either "UP" or "DOWN")
        self.touch_state = None
        # The last position on the screen that was touched
        self.current_pos = (-1, -1)

        # Grab the display device file
        os.putenv('SDL_FBDEV', '/dev/fb1')
        # Grab the mouse device files
        os.putenv('SDL_MOUSEDRV', 'TSLIB')
        os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

        # Start the pygame engine
        pygame.init()

        # Turn off the mouse cursor and erase the screen
        pygame.mouse.set_visible(False)
        self.lcd = pygame.display.set_mode(self.size)
        self.lcd.fill((0, 0, 0))
        pygame.display.update()

    def update(self, input_image):
        """Grab any touch screen input and update the screen with the input
        image.

        Args:
            input_image(numpy.ndarray): The image to show on the screen for
            this update.

        Return:
            Tuple of a string representing the touch screen state (either "UP"
            or "DOWN") and the last position on the touch screen that was
            touched.
        """
        # Scan touchscreen events
        for event in pygame.event.get():
            self.current_pos = pygame.mouse.get_pos()
            if event.type is MOUSEBUTTONDOWN:
                self.touch_state = self.TOUCH_UP
            elif event.type is MOUSEBUTTONUP:
                self.touch_state = self.TOUCH_DOWN

        self.lcd.blit(pygame.surfarray.make_surface(input_image), (0, 0))
        pygame.display.update()

        return self.current_pos, self.current_pos
