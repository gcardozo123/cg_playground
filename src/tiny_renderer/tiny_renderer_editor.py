import time

import imgui

from scene import Scene
from tiny_renderer.tiny_renderer import LightingMode, RenderingMode, TinyRenderer


class TinyRendererEditor(Scene):
    def __init__(self):
        self._render_mode_captions = RenderingMode.get_captions()
        self._render_mode = RenderingMode.Wireframe

        self._light_mode_captions = LightingMode.get_captions()
        self._light_mode = LightingMode.Flat

        self._model = TinyRenderer()
        self._time_to_render = 0

    def on_click_render(self):
        self._model.render(self._render_mode, self._light_mode)

    def update(self):
        bitmap = self._model.bitmap
        if bitmap is None:
            return

        imgui.begin("Tiny Renderer")

        imgui.image(bitmap.get_texture_id(), bitmap.get_width(), bitmap.get_height())
        imgui.end()

        imgui.begin("Rendering")
        _, self._render_mode = imgui.combo(
            "Rendering Mode", self._render_mode, self._render_mode_captions
        )
        _, self._light_mode = imgui.combo(
            "Lighting Mode", self._light_mode, self._light_mode_captions
        )

        imgui.separator()
        if imgui.button("Render"):
            t = time.time()
            self.on_click_render()
            self._time_to_render = time.time() - t

        imgui.label_text("", f"Time to render: {self._time_to_render: .2f}s")
        imgui.separator()

        imgui.end()
