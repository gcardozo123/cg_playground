import glfw
import imgui
import OpenGL.GL as gl
from imgui.integrations.glfw import GlfwRenderer

from tiny_renderer.tiny_renderer import TinyRenderer


class Application:
    def __init__(self, args):
        imgui.create_context()
        self._window = self._glfw_init()
        self._renderer = GlfwRenderer(self._window)
        self._scene = TinyRenderer()
        self.main_loop()

    def main_loop(self):
        while not glfw.window_should_close(self._window):
            glfw.poll_events()
            self._renderer.process_inputs()

            imgui.new_frame()

            gl.glClearColor(0.2, 0.2, 0.2, 1.0)
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)

            self._scene.update()

            imgui.render()
            self._renderer.render(imgui.get_draw_data())
            glfw.swap_buffers(self._window)

        self._renderer.shutdown()
        glfw.terminate()

    def _glfw_init(self):
        """
        Initializes the glfw an OpenGL context and returns a window
        """
        width, height = 1600, 900
        window_name = "Computer Graphics Playground"

        if not glfw.init():
            print("Could not initialize OpenGL context")
            exit(1)

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        # Create a windowed mode window and its OpenGL context
        window = glfw.create_window(int(width), int(height), window_name, None, None)
        glfw.make_context_current(window)

        if not window:
            glfw.terminate()
            print("Could not initialize Window")
            exit(1)

        return window
