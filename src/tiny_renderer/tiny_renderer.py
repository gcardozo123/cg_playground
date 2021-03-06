import random
from collections import namedtuple
from enum import IntEnum
from pathlib import Path
from typing import Sequence, Union

import numpy as np
from PIL import Image

from math_utils import Vec2, Vec3, apply_weights
from tiny_renderer.bitmap import Bitmap
from tiny_renderer.model import Model

Color = namedtuple("Color", "r g b a")


class Colors:
    White = Color(255, 255, 255, 255)
    Red = Color(255, 0, 0, 255)
    Green = Color(0, 255, 0, 255)
    Blue = Color(0, 0, 255, 255)


class LightingMode(IntEnum):
    """
    Lighting mode for `TinyRenderer`
    """

    Smooth = 0
    Flat = 1

    @classmethod
    def get_caption(cls, index):
        captions = {
            cls.Smooth: "Smooth",
            cls.Flat: "Flat",
        }
        return captions[index]

    @classmethod
    def get_captions(cls):
        return [LightingMode.get_caption(i) for i in LightingMode]


class RenderingMode(IntEnum):
    """
    Possible rendering modes for `TinyRenderer`
    """

    Wireframe = 0
    RandomColors = 1
    Texturized = 2
    LightOnly = 3

    @classmethod
    def get_caption(cls, index):
        captions = {
            cls.Wireframe: "Wireframe",
            cls.RandomColors: "Random color",
            cls.Texturized: "Texturized",
            cls.LightOnly: "Light only",
        }
        return captions[index]

    @classmethod
    def get_captions(cls):
        return [RenderingMode.get_caption(i) for i in RenderingMode]


class TinyRenderer:
    """
    My own version of the original Tiny Renderer:
    https://github.com/ssloy/tinyrenderer/wiki
    """

    def __init__(self, *, bind_texture=True):
        """
        :param bind_texture:
            If `True`, `TinyRenderer` will create a `tiny_renderer.bitmap.Bitmap` instance
            binding any rendered image to an OpenGL texture. This can be disabled for tests
            so they don't need to initialize an OpenGL context.
        """
        self._height = 800
        self._width = 800
        self._depth = 800

        self._scale_x = 1.0
        self._scale_y = 1.0
        self._scale_z = 1.0

        self._image = np.zeros((self._height, self._width, 3), np.uint8)
        self._z_buffer = np.full((self._height, self._width, 1), np.inf)
        self._camera_postion = Vec3(0, 0, -1)
        self._model = None
        self.set_scale(0.45, 0.45, 0.45)

        self._render_mode = None
        self._light_mode = None
        self._bind_texture = bind_texture
        self._bitmap = Bitmap(self.get_image()) if bind_texture else None
        self._texture_image = None

    def setup_model(self, model_filename: Union[str, Path], texture_filename: Union[str, Path]):
        """
        Defines a model (.obj) and texture for this `TinyRenderer`.
        """
        self.load_model(Path(model_filename))
        self._texture_image = np.flipud(Image.open(texture_filename))[..., ::-1]

    @property
    def bitmap(self) -> Bitmap:
        return self._bitmap

    def render(self, render_mode: RenderingMode, light_mode: LightingMode):
        self.clear()

        self._render_mode = render_mode
        self._light_mode = light_mode
        self._rasterize()
        if self._bind_texture:
            self._bitmap.bind_texture(pixels=self.get_image())

    def clear(self):
        self._image = np.zeros((self._height, self._width, 3), np.uint8)
        self._z_buffer = np.full((self._height, self._width, 1), np.inf)

    def set_scale(self, x, y, z):
        self._scale_x = x
        self._scale_y = y
        self._scale_z = z

    def load_model(self, filename):
        self._model = Model()
        self._model.load_from_obj(filename)

    def _draw_wireframe(self):
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
                self.draw_line(Vec3(x0, y0), Vec3(x1, y1), Colors.White, Colors.White)

    def _rasterize(self):
        if self._render_mode == RenderingMode.Wireframe:
            self._draw_wireframe()
            return

        for i in range(self._model.num_faces()):
            face = self._model.get_face_at(i)
            verts = [self._model.get_vertex_at(face[x]) for x in range(3)]
            uvs = self._model.get_uvs_from_face(i)
            # scale the model
            verts = [
                Vec3(
                    (v[0] + 1.0) * (self._width * self._scale_x),
                    (v[1] + 1.0) * (self._height * self._scale_y),
                    (v[2] + 1.0) * (self._depth * self._scale_z),
                )
                for v in verts
            ]
            light_dir = self._camera_postion
            normals = self._model.get_normals_from_face(i)
            vertices = (
                Vec3(round(verts[0].x), round(verts[0].y), verts[0].z),
                Vec3(round(verts[1].x), round(verts[1].y), verts[1].z),
                Vec3(round(verts[2].x), round(verts[2].y), verts[2].z),
            )
            self.draw_triangle(
                vertices, uvs, normals, light_dir,
            )

    def _get_rgb_from_uv(self, uv: tuple) -> tuple:
        """
        Returns the RGB color for an (u,v) normalized coordinate for `self._texture_image`
        """
        u, v = uv
        height, width = self._texture_image.shape[0], self._texture_image.shape[1]
        u_index = round(u * width)
        v_index = round(v * height)
        # reverse because values are stored as BGR:
        return tuple(reversed(self._texture_image[v_index][u_index]))

    def get_image(self):
        return np.flipud(self._image)

    def save_image(self, filename):
        """
        :param filename:
            Complete path to the image including the extension
        """
        assert filename.parent.is_dir()
        Image.fromarray(self._image).save(filename)

    def draw_line(self, v0: Vec3, v1: Vec3, c0: Color, c1: Color):
        """
        Draws a line to `self._image`, from (x0, y0) to (x1, y1) using Bresenham's algorithm
        """
        if v0 == v1:
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
            v0, v1 = v1, v0
            c0, c1 = c1, c0

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
            c0, c1 = (c1, c0) if steep else (c0, c1)

            if distance_to_camera < self._z_buffer[pixel_y, pixel_x]:
                self._z_buffer[pixel_y, pixel_x] = distance_to_camera

                color = Color(
                    c0.r * percentage + c1.r * (1 - percentage),
                    c0.g * percentage + c1.g * (1 - percentage),
                    c0.b * percentage + c1.b * (1 - percentage),
                    255,
                )
                self.set_pixel(pixel_x, pixel_y, color)

            error += d_error
            if error > 0.5:
                y += 1 if v1.y > v0.y else -1
                error -= 1

    def set_pixel(self, x, y, color):
        row = y
        col = x
        self._image[row, col] = (color.r, color.g, color.b)

    def draw_triangle(
        self,
        vertices: Sequence[Vec3],
        uvs: Sequence[Vec2],
        normals: Sequence[Vec2],
        light_direction: Vec3,
    ):
        """
        Draws a triangle into self._image
        """
        p0, p1, p2 = vertices
        if (p0 in (p1, p2)) or (p1 == p2):
            # triangle is degenerated
            return

        uv0, uv1, uv2 = uvs
        n0, n1, n2 = normals

        if self._light_mode == LightingMode.Flat:
            edge = p2.sub(p0)
            other_edge = p1.sub(p0)
            final_normal = edge.cross(other_edge).normalized()

        if self._render_mode == RenderingMode.LightOnly:
            final_color = Colors.White
        elif self._render_mode == RenderingMode.RandomColors:
            final_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # create 4 points representing the bounding box of the triangle
        min_x = min(p0.x, min(p1.x, p2.x))
        max_x = max(p0.x, max(p1.x, p2.x))
        min_y = min(p0.y, min(p1.y, p2.y))
        max_y = max(p0.y, max(p1.y, p2.y))

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                p = Vec2(x, y)

                barycentric_weights = Vec2.obtain_barycentric_weights(p, p0, p1, p2)
                is_part_of_triangle = all(w >= 0 for w in barycentric_weights)
                if not is_part_of_triangle:
                    continue

                p3d = Vec3(p.x, p.y, round(apply_weights([p0.z, p1.z, p2.z], barycentric_weights)))

                distance_to_camera = p3d.distance(self._camera_postion)
                if distance_to_camera > self._z_buffer[y, x]:
                    # ignore hidden pixel
                    continue
                self._z_buffer[y, x] = distance_to_camera

                if self._render_mode == RenderingMode.Texturized:
                    final_uv = (
                        apply_weights([uv0.x, uv1.x, uv2.x], barycentric_weights),
                        apply_weights([uv0.y, uv1.y, uv2.y], barycentric_weights),
                    )
                    final_color = self._get_rgb_from_uv(final_uv)

                if self._light_mode == LightingMode.Smooth:
                    final_normal = Vec3(
                        apply_weights([n0.x, n1.x, n2.x], barycentric_weights),
                        apply_weights([n0.y, n1.y, n2.y], barycentric_weights),
                        apply_weights([n0.z, n1.z, n2.z], barycentric_weights),
                    )

                light_intensity = abs(light_direction.dot(final_normal))
                self.set_pixel(
                    x,
                    y,
                    Color(
                        final_color[0] * light_intensity,
                        final_color[1] * light_intensity,
                        final_color[2] * light_intensity,
                        255,
                    ),
                )
