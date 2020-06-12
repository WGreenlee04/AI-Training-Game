from pathlib import Path

import pyglet
from pyglet.gl import *

pyglet.options['search_local_libs'] = True

__sprite_path = Path("resources/sprites")
__media_path = Path("resources/media")


# main function
def main():
	window = pyglet.window.Window(1920, 1080)
	window.set_location(0, 0)
	window.set_fullscreen(True)
	window.set_caption("ShooterGame")

	label = pyglet.text.Label('Hello, world', font_name='Times New Roman', font_size=36,
	                          x=window.width // 2, y=window.height // 2,
	                          anchor_x='center', anchor_y='center')
	window_icon = pyglet.image.load(str(__sprite_path.joinpath("logo320x320.png").absolute()))
	test_music = pyglet.media.load(str(__media_path.joinpath("Fluffing a Duck.wav").absolute()))

	window.set_icon(window_icon)
	test_music.play()

	@window.event
	def on_draw():
		window.clear()
		label.draw()

	pyglet.app.run()
