from collections import namedtuple
from pathlib import Path

import numpy as np
from scene import Scene
import cv2
from tiny_renderer.model import Model

Color = namedtuple("Color", "r g b a")

class TinyRenderer(Scene):
    """
    My own version of the original Tiny Renderer:
    https://github.com/ssloy/tinyrenderer/wiki
    """
    def __init__(self):
        self._image_directory = Path('../resources/images/')
        assert self._image_directory.is_dir()

        self._height = 800
        self._width = 800
        self._image = np.zeros((self._height, self._width, 3), np.uint8)

        self.white = Color(255, 255, 255, 2555)
        self.red = Color(255, 0, 0, 2555)

        self._load_model()
        self.display_image()

    def _load_model(self):
        model = Model()
        model.load_from_obj("../resources/african_head.obj")
        for i in range(model.num_faces()):
            face = model.get_face_at(i)
            for j in range(3):
                v0 = model.get_vertex_at(face[j])
                v1 = model.get_vertex_at(face[(j + 1) % 3])
                # scale down the model
                x0 = (v0[0] + 1.0) * (self._width * 0.45)
                y0 = (v0[1] + 1.0) * (self._height * 0.45)
                x1 = (v1[0] + 1.0) * (self._width * 0.45)
                y1 = (v1[1] + 1.0) * (self._height * 0.45)

                x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
                if (x0, y0) == (x1, y1):
                    continue
                self.line(x0, y0, x1, y1, self.white)

    def update(self):
        pass

    def get_image(self):
        return np.flipud(self._image)

    def display_image(self):
        cv2.namedWindow('Tiny Renderer', cv2.WINDOW_AUTOSIZE)
        # flip the image vertically so the origin is at the left bottom corner of the image
        # just because the original tiny renderer uses this origin ¯\_(ツ)_/¯
        cv2.imshow('Tiny Renderer', np.flipud(self._image))

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

    def set_pixel(self, x, y, color):
        row = y
        col = x
        self._image[row, col] = (color.b, color.g, color.r)

    def image_to_1_bit_array(self):
        # todo fix this: for now it only checks the blue coordinate (index 0)
        return self._image[:,:,0] > 0

