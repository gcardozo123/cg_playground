from collections import namedtuple
from pathlib import Path

import cv2
import imgui
import numpy as np

from math_utils import Vec2, Vec3
from scene import Scene
from tiny_renderer.bitmap import Bitmap
from tiny_renderer.model import Model

Color = namedtuple("Color", "r g b a")


class TinyRenderer(Scene):
    """
    My own version of the original Tiny Renderer:
    https://github.com/ssloy/tinyrenderer/wiki
    """

    def __init__(self):
        self._image_directory = Path("../resources/images/")
        assert self._image_directory.is_dir()

        self._height = 800
        self._width = 800
        self._depth = 800

        self._scale_x = 1.0
        self._scale_y = 1.0
        self._scale_z = 1.0

        self._image = np.zeros((self._height, self._width, 3), np.uint8)
        self._model = None

        self.white = Color(255, 255, 255, 255)
        self.red = Color(255, 0, 0, 255)
        self.green = Color(0, 255, 0, 255)
        self.blue = Color(0, 0, 255, 255)

        self.set_scale(0.45, 0.45, 0.45)
        self.load_model("../resources/african_head.obj")
        self._fill_triangles()
        self._bitmap = Bitmap(self.get_image())

    def clear_image(self):
        self._image = np.zeros((self._height, self._width, 3), np.uint8)

    def set_scale(self, x, y, z):
        self._scale_x = x
        self._scale_y = y
        self._scale_z = z

    def load_model(self, filename):
        self._model = Model()
        self._model.load_from_obj(filename)

    def wireframe(self):
        for i in range(self._model.num_faces()):
            face = self._model.get_face_at(i)
            for j in range(3):
                v0 = self._model.get_vertex_at(face[j])
                v1 = self._model.get_vertex_at(face[(j + 1) % 3])
                # scale down the model
                x0 = (v0[0] + 1.0) * (self._width * self._scale_x)
                y0 = (v0[1] + 1.0) * (self._height * self._scale_y)
                x1 = (v1[0] + 1.0) * (self._width * self._scale_x)
                y1 = (v1[1] + 1.0) * (self._height * self._scale_y)

                x0, y0, x1, y1 = round(x0), round(y0), round(x1), round(y1)
                self.line(x0, y0, x1, y1, self.white)

    def _fill_triangles(self):
        for i in range(self._model.num_faces()):
            face = self._model.get_face_at(i)
            verts = [self._model.get_vertex_at(face[x]) for x in range(3)]
            # scale the model
            verts = [
                Vec3(
                    (v[0] + 1.0) * (self._width * self._scale_x),
                    (v[1] + 1.0) * (self._height * self._scale_y),
                    (v[2] + 1.0) * (self._depth * self._scale_z),
                )
                for v in verts
            ]
            edge = verts[2].sub(verts[0])
            other_edge = verts[1].sub(verts[0])
            face_normal = edge.cross(other_edge).normalized()

            light_dir = Vec3(0, 0, -1)
            intensity = light_dir.dot(face_normal)

            if intensity > 0:
                color = Color(255 * intensity, 255 * intensity, 255 * intensity, 255)
                self.triangle(
                    Vec2(round(verts[0].x), round(verts[0].y)),
                    Vec2(round(verts[1].x), round(verts[1].y)),
                    Vec2(round(verts[2].x), round(verts[2].y)),
                    color,
                )

    def update(self):
        if not self._bitmap:
            return

        imgui.begin("Tiny Renderer")
        imgui.image(
            self._bitmap.get_texture_id(), self._bitmap.get_width(), self._bitmap.get_height()
        )
        imgui.end()

    def get_image(self):
        return np.flipud(self._image)

    def display_image(self):
        """
        Displays the image on a separate openCV window
        """
        cv2.namedWindow("Tiny Renderer", cv2.WINDOW_AUTOSIZE)
        # flip the image vertically so the origin is at the left bottom corner of the image
        # just because the original tiny renderer uses this origin ¯\_(ツ)_/¯
        cv2.imshow("Tiny Renderer", np.flipud(self._image))

    def save_image(self, filename):
        """
        :param filename:
            Complete path to the image including the extension
        """
        assert filename.parent.is_dir()
        cv2.imwrite(str(filename), self._image)

    def line(self, x0, y0, x1, y1, color: Color):
        """
        Draws a line from (x0, y0) to (x1, y1) using Bresenham's algorithm
        """
        if (x0, y0) == (x1, y1):
            # This is a point, not a line.
            return

        steep = False
        # if the line is steep, we transpose the image
        if abs(x0 - x1) < abs(y0 - y1):
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
            dx = 0.000001  # just to prevent zero division error
        derror = abs(dy / dx)
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
        self._image[row, col] = (color.r, color.g, color.b)

    def image_to_1_bit_array(self):
        # todo fix this: for now it only checks the blue coordinate (index 0)
        return self._image[:, :, 0] > 0

    def triangle(self, p0: Vec2, p1: Vec2, p2: Vec2, color: Color):
        """
        Draws a triangle into self._image
        """
        if not self._is_counterclockwise(p0, p1, p2):
            p0, p1, p2 = (p0, p2, p1) if self._is_counterclockwise(p0, p2, p1) else (p1, p0, p2)

        # create 4 points representing the bounding box of the triangle
        min_x = min(p0.x, min(p1.x, p2.x))
        max_x = max(p0.x, max(p1.x, p2.x))
        min_y = min(p0.y, min(p1.y, p2.y))
        max_y = max(p0.y, max(p1.y, p2.y))

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = Vec2(x, y)
                is_inside_triangle = True
                for edge in [(p0, p1), (p1, p2), (p2, p0)]:
                    if not self._is_left(p, edge[0], edge[1]):
                        is_inside_triangle = False
                        break
                if is_inside_triangle:
                    self.set_pixel(x, y, color)

        # draw the triangle border
        self.line(p0.x, p0.y, p2.x, p2.y, color)
        self.line(p0.x, p0.y, p1.x, p1.y, color)
        self.line(p1.x, p1.y, p2.x, p2.y, color)

    def _triangle_area(self, p0, p1, p2):
        """
        Returns twice the area - just to avoid division - of the oriented triangle (p0, p1, p2).
        The area is positive if the triangle is oriented counterclockwise.
        """
        return (p1.x - p0.x) * (p2.y - p0.y) - (p1.y - p0.y) * (p2.x - p0.x)

    def _is_counterclockwise(self, p0, p1, p2):
        """
        Returns true if the Vec2s p0, p1, p2 are in a counterclockwise order
        """
        return self._triangle_area(p0, p1, p2) > 0

    def _is_left(self, p0, p1, p2):
        """
        Returns True if p0 is on the left of the line p2 - p1.
        p ^ <- p is on the left side of the line
         /
        /
        """
        return self._triangle_area(p0, p1, p2) > 0
