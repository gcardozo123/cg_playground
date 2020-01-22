from collections import namedtuple
from pathlib import Path

import imgui
import numpy as np

import cv2
from math_utils import Vec2, Vec3
from scene import Scene
from tiny_renderer.bitmap import Bitmap
from tiny_renderer.model import Model

Color = namedtuple("Color", "r g b a")


class Colors:
    WHITE = Color(255, 255, 255, 255)
    RED = Color(255, 0, 0, 255)
    GREEN = Color(0, 255, 0, 255)
    BLUE = Color(0, 0, 255, 255)


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
        self._z_buffer = np.full((self._height, self._width, 1), np.NINF)
        self._camera_postion = Vec3(0, 0, -1)
        self._model = None

        self.set_scale(0.45, 0.45, 0.45)
        self.load_model("../resources/african_head.obj")
        self._rasterize_triangles()
        self._bitmap = Bitmap(self.get_image())

    def clear_image(self):
        self._image = np.zeros((self._height, self._width, 3), np.uint8)
        self._z_buffer = np.full((self._height, self._width, 1), np.inf)

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
                self.line(Vec3(x0, y0), Vec3(x1, y1), Colors.WHITE)

    def _rasterize_triangles(self):
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
                    Vec3(round(verts[0].x), round(verts[0].y), round(verts[0].z)),
                    Vec3(round(verts[1].x), round(verts[1].y), round(verts[1].z)),
                    Vec3(round(verts[2].x), round(verts[2].y), round(verts[2].z)),
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

    def line(self, v0: Vec3, v1: Vec3, color: Color = Colors.WHITE):
        """
        Draws a line from (x0, y0) to (x1, y1) using Bresenham's algorithm
        """
        v0, v1 = Vec3.clone(v0), Vec3.clone(v1)
        if (v0.x, v0.y) == (v1.x, v1.y):
            # This is a point, not a line.
            return

        steep = False
        # if the line is steep, we transpose the image
        if v0.dx(v1) < v0.dy(v1):
            v0.x, v0.y = v0.y, v0.x
            v1.x, v1.y = v1.y, v1.x
            steep = True

        dx = v0.dx(v1)
        dy = v0.dy(v1)
        # make sure it goes from left to right:
        if v0.x > v1.x:
            v0.x, v1.x = v1.x, v0.x
            v0.y, v1.y = v1.y, v0.y

        if dx == 0:
            dx = 0.000001  # just to prevent zero division error

        # dy/dx is the slope or gradient of the line (or coeficiente angular in portuguese)
        # if dy/dx > 0, then the line goes up: /
        # if dy/dx < 0, then the line goes down: \
        # if a line is horizontal the slope is zero
        # if a line is vertical the slope is undefined
        d_error = abs(dy / dx)
        error = 0
        y = v0.y
        for x in range(v0.x, v1.x + 1):
            p = Vec3(x, y, 0)
            distance_p_v0 = p.distance_2d(v0)
            distance_v0_v1 = v0.distance_2d(v1)

            percentage = distance_p_v0 / distance_v0_v1
            dz = v0.dz(v1)
            p.z = v0.z + (dz * percentage)

            distance_to_camera = p.distance(self._camera_postion)

            # if transposed, de−transpose
            pixel_x, pixel_y = (p.y, p.x) if steep else (p.x, p.y)

            if distance_to_camera > self._z_buffer[pixel_y, pixel_x]:
                self._z_buffer[pixel_y, pixel_x] = distance_to_camera
                self.set_pixel(pixel_x, pixel_y, color)

            error += d_error
            if error > 0.5:
                y += 1 if v1.y > v0.y else -1
                error -= 1

    def set_pixel(self, x, y, color):
        row = y
        col = x
        self._image[row, col] = (color.r, color.g, color.b)

    def image_to_1_bit_array(self):
        # todo fix this: for now it only checks the blue coordinate (index 0)
        return self._image[:, :, 0] > 0

    def triangle(self, p0: Vec3, p1: Vec3, p2: Vec3, color: Color):
        """
        Draws a triangle into self._image
        """
        if not Vec3.is_counterclockwise(p0, p1, p2):
            p0, p1, p2 = (p0, p2, p1) if Vec3.is_counterclockwise(p0, p2, p1) else (p1, p0, p2)

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
                    if not Vec3.is_left(p, edge[0], edge[1]):
                        is_inside_triangle = False
                        break
                if is_inside_triangle:
                    p3d = Vec3(x, y, Vec3.interpolate_z(Vec3(x, y), p0, p1, p2))
                    distance_to_camera = p3d.distance(self._camera_postion)
                    if distance_to_camera > self._z_buffer[y, x]:
                        self._z_buffer[y, x] = distance_to_camera
                        self.set_pixel(x, y, color)

        # draw the triangle border
        self.line(p0, p2, color)
        self.line(p0, p1, color)
        self.line(p1, p2, color)
