
import bimpy
from gl_playground.gl_basics import GLBasics
from tiny_renderer.tiny_renderer import TinyRenderer


class  Application:
    def __init__(self, args):
        ctx = bimpy.Context()
        ctx.init(800, 600, "Computer Graphics Playground")
        scene = TinyRenderer(ctx)
        while not ctx.should_close():
            ctx.new_frame()
            #bimpy.begin("Menu")
            scene.update()
            #bimpy.end()
            ctx.render()

