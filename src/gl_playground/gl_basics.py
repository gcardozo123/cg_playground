from pathlib import Path

import numpy as np
from OpenGL.GL import *

from scene import Scene


def clear_gl_errors():
    while glGetError() != GL_NO_ERROR:
        continue


def check_gl_errors():
    error = glGetError()
    while error:
        print(error)
        error = glGetError()


def gl_debug_callback(source, msg_type, msg_id, severity, length, raw, user):
    msg = raw[0:length]
    print("debug", source, msg_type, msg_id, severity, msg)


class GLBasics(Scene):
    def __init__(self):
        print("OpenGL version: ", glGetString(GL_VERSION))

        self._build_geometry()
        self._compile_shaders()
        glDebugMessageCallback(GLDEBUGPROC(gl_debug_callback), None)

    def update(self):
        glClearColor(0.3, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        glFlush()

    def _build_geometry(self):
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        # fmt: off
        verts = np.array([
            -1.0, -1.0, 0.0, # p0
            1.0, -1.0, 0.0,  # p1
            1.0, 1.0, 0.0,   # p2
            -1.0, 1.0, 0.0   # p3
            ],
            dtype=np.float32,
        )
        # fmt: on
        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, verts, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(
            0,  # index
            3,  # size (components)
            GL_FLOAT,  # type
            GL_FALSE,  # normalized
            0,  # stride
            None,  # pointer
        )
        elements = np.array([0, 1, 2, 0, 2, 3], dtype=np.int32)

        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, elements, GL_STATIC_DRAW)

    def _compile_shaders(self):
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        self._compile_shader_source(vertex_shader, "gl_playground/shaders/shader.vert")

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        self._compile_shader_source(fragment_shader, "gl_playground/shaders/shader.frag")

        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        glLinkProgram(program)
        glValidateProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            raise RuntimeError(glGetProgramInfoLog(program))

        glUseProgram(program)
        # glDeleteShader(vertex_shader)
        # glDeleteShader(fragment_shader)

    def _compile_shader_source(self, shader_id, shader_path):
        contents = Path(shader_path).read_text()
        clear_gl_errors()
        glShaderSource(shader_id, contents)
        check_gl_errors()
        glCompileShader(shader_id)
        compile_ok = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if not compile_ok:
            raise RuntimeError(glGetShaderInfoLog(shader_id))
