from collections import namedtuple
from pathlib import Path

import numpy as np
from scene import Scene
import cv2

Color = namedtuple("Color", "r g b a")

class TinyRenderer(Scene):
    """
    My own version of the original Tiny Renderer:
    https://github.com/ssloy/tinyrenderer/wiki
    """
    def __init__(self, imgui_ctx):
        self._imgui = imgui_ctx

        self._image_directory = Path('../resources/images/')
        assert self._image_directory.is_dir()

        self._height = 300
        self._width = 200
        self._image = np.zeros((self._height, self._width, 3), np.uint8)

        #self._image[:, 0:self._width // 2] = (255, 0, 0)  # (B, G, R)
        #self._image[:, self._width // 2:self._width] = (0, 255, 0)

        white = Color(255, 255, 255, 2555)
        red = Color(255, 0, 0, 2555)
        self.line(13, 20, 80, 40, white)
        self.line(80, 40, 13, 20, red)
        self.line(20, 13, 40, 80, white)

        #res = self.image_to_1_bit_array()
        self.display_image()

    def update(self):
        pass

    def display_image(self):
        # flip the image vertically so the origin is at the left bottom corner of the image
        # just because the original tiny renderer uses this origin ¯\_(ツ)_/¯
        cv2.imshow('image', np.flipud(self._image))

    def save_image(self, filename):
        """
        :param filename:
            Complete path to the image including the extension
        """
        assert filename.parent.is_dir()
        cv2.imwrite(str(filename), self._image)

    def line(self, x0, y0, x1, y1, color:Color):
        """
        Draws a line from (x0, y0) to (x1, y1) using Bresenham's algorithm
        """
        if (x0, y0) == (x1, y1):
            raise ValueError("This is a point, not a line. Use set_pixel instead.")

        steep = False
        # if the line is steep, we transpose the image
        if abs(x0-x1) < abs(y0-y1):
            x0, y0 = y0, x0
            x1, y1 = y1, x1
            steep = True

        # make sure it goes from left to right:
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dx = x1 - x0
        dy = y1 - y0
        # dy/dx is the slope or gradient of the line (or coeficiente angular in portuguese)
        # if dy/dx > 0, then the line goes up: /
        # if dy/dx < 0, then the line goes down: \
        # if a line is horizontal the slope is zero
        # if a line is vertical the slope is undefined
        if dx == 0:
            dx = 0.000001 # just to prevent zero division error
        derror = abs(dy/dx)
        error = 0
        y = y0
        for x in range(x0, x1 + 1):
            if steep:
                # if transposed, de−transpose
                self.set_pixel(y, x, color)
            else:
                self.set_pixel(x, y, color)
            error += derror
            if error > 0.5:
                y += 1 if y1 > y0 else -1
                error -= 1

        # for each column between x0, x1 there's exactly one row, i.e., the x coordinate
        # will never be repeated, it always increases one by one, so we need to calculate y:
        # for x in range(x0, x1 + 1):
        #     t = (x - x0) / (x1 - x0)
        #     y = y0 * (1 - t) + y1 * t
        #
        #     y = round(y)
        #     if steep:
        #         # if transposed, de−transpose
        #         self.set_pixel(y, x, color)
        #     else:
        #         self.set_pixel(x, y, color)

    def set_pixel(self, x, y, color):
        row = y
        col = x
        self._image[row, col] = (color.b, color.g, color.r)

    def image_to_1_bit_array(self):
        # todo fix this: for now it only checks the blue coordinate (index 0)
        return self._image[:,:,0] > 0

