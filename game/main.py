import pyglet
from pyglet.gl import *


# main function
def main():
	window = pyglet.window.Window(1920, 1080)
	label = pyglet.text.Label('Hello, world', font_name='Times New Roman', font_size=36,
	                          x=window.width // 2, y=window.height // 2,
	                          anchor_x='center', anchor_y='center')
	window.set_location(0, 0)
	window.set_fullscreen(True)
	window.set_caption("ShooterGame")

	@window.event
	def on_draw():
		window.clear()
		label.draw()

	pyglet.app.run()
