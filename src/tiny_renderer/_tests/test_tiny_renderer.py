import pytest
from PIL import Image

from tiny_renderer.tiny_renderer import LightingMode, RenderingMode, TinyRenderer


@pytest.fixture
def renderer(datadir):
    result = TinyRenderer(bind_texture=False)
    result.setup_model(
        datadir / "african_head.obj", datadir / "african_head_diffuse.jpg",
    )
    return result


@pytest.mark.parametrize("render_mode", [x for x in RenderingMode])
@pytest.mark.parametrize("light_mode", [x for x in LightingMode])
def test_tiny_renderer_images(datadir, image_regression, renderer, render_mode, light_mode):
    renderer.render(render_mode, light_mode)
    image_basename = f"{render_mode.name}_{light_mode.name}"
    image_filename = datadir / f"{image_basename}.png"

    Image.fromarray(renderer.get_image()).save(image_filename)
    image_regression.check(image_filename.read_bytes(), basename=image_basename)
