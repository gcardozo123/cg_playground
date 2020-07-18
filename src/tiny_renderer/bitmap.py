import numpy as np
from OpenGL.GL import *


class Bitmap:
    """
    A bitmap that Imgui understands.
    Usage:
        image = Bitmap(pixels)
        # inside the rendering loop:
        imgui.begin("Image")
        imgui.image(image.get_texture_id(), image.get_width(), image.get_height())
        imgui.end()
    """

    def __init__(self, pixels: np.array):
        self._texture_id = glGenTextures(1)
        self._width = -1
        self._height = -1
        self._pixels = pixels

    def bind_texture(self, *, pixels: np.array = None):
        if pixels is None:
            pixels = self._pixels

        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        backup = glGetIntegerv(GL_UNPACK_ALIGNMENT)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

        swizzleMask_R = [GL_RED, GL_RED, GL_RED, GL_ONE]
        swizzleMask_RG = [GL_RED, GL_GREEN, GL_ZERO, GL_ONE]
        swizzleMask_RGB = [GL_RED, GL_GREEN, GL_BLUE, GL_ONE]
        swizzleMask_RGBA = [GL_RED, GL_GREEN, GL_BLUE, GL_ALPHA]

        self._width = pixels.shape[1]
        self._height = pixels.shape[0]

        if pixels.ndim == 2:
            glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask_R)
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_R8,
                self._width,
                self._height,
                0,
                GL_RED,
                GL_UNSIGNED_BYTE,
                pixels,
            )

        elif pixels.ndim == 3:
            self._width = pixels.shape[1]
            self._height = pixels.shape[0]

            if pixels.shape[2] == 1:
                glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask_R)
                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_R8,
                    self._width,
                    self._height,
                    0,
                    GL_RGB,
                    GL_UNSIGNED_BYTE,
                    pixels,
                )

            elif pixels.shape[2] == 2:
                glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask_RG)
                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RG8,
                    self._width,
                    self._height,
                    0,
                    GL_RG,
                    GL_UNSIGNED_BYTE,
                    pixels,
                )

            elif pixels.shape[2] == 3:
                glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask_RGB)
                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RGB8,
                    self._width,
                    self._height,
                    0,
                    GL_RGB,
                    GL_UNSIGNED_BYTE,
                    pixels,
                )

            elif pixels.shape[2] == 4:
                glTexParameteriv(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_RGBA, swizzleMask_RGBA)
                glTexImage2D(
                    GL_TEXTURE_2D,
                    0,
                    GL_RGBA8,
                    self._width,
                    self._height,
                    0,
                    GL_RGBA,
                    GL_UNSIGNED_BYTE,
                    pixels,
                )

            else:
                glBindTexture(GL_TEXTURE_2D, 0)
                glPixelStorei(GL_UNPACK_ALIGNMENT, backup)
                raise RuntimeError("Wrong number of channels. Should be either 1, 2, 3, or 4")
        else:
            glBindTexture(GL_TEXTURE_2D, 0)
            glPixelStorei(GL_UNPACK_ALIGNMENT, backup)
            raise RuntimeError("Wrong number of dimensions. Should be either 2 or 3")

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        glPixelStorei(GL_UNPACK_ALIGNMENT, backup)
        glBindTexture(GL_TEXTURE_2D, 0)

    def get_texture_id(self):
        return self._texture_id

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def dispose(self):
        glDeleteTextures(1, self._texture_id)
