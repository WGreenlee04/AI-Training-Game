import pyglet
from pyglet import clock
from pyglet import resource
from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.window import Window
from pyglet.window import key

from game.level import Level, Player, BlockPlace
from game.settings import Settings


# NOTES:
# One Player is exactly 1 meter tall.


class KeyStateHandler(dict):
	"""Simple handler that tracks the state of keys on the keyboard. If a
	key is pressed then this handler holds a True value for it.

	For example::

		>>win = window.Window
		>> keyboard = key.KeyStateHandler()
		>> win.push_handlers(keyboard)

		# Hold down the "up" arrow...

		>> keyboard[key.UP]
		True
		>> keyboard[key.DOWN]
		False

	"""

	def on_key_press(self, symbol, modifiers):
		self[key.symbol_string(symbol)] = True

	def on_key_release(self, symbol, modifiers):
		self[key.symbol_string(symbol)] = False

	def __getitem__(self, symbol):
		return self.get(symbol, False)


def main():
	"""
	Main function
		:return: Exits the game
	"""

	Settings.set_default()
	Settings.save()
	Settings.load()

	Settings.pyglet_reindex(Settings.global_resource_sub_folders)  # tell pyglet where to look for resources
	Settings.global_main_window = Window(width=int(Settings.settings['window_resolution'].split('x')[0]),
	                                     height=int(Settings.settings['window_resolution'].split('x')[1]),
	                                     caption='ShooterGame',
	                                     vsync=str(Settings.settings['vsync']).lower() == 'on',
	                                     fullscreen=str(Settings.settings['window_style']).lower() == 'fullscreen',
	                                     visible=False)
	Settings.global_main_window.set_icon(resource.image('logo.png'))  # further window config

	game(window=Settings.global_main_window, level=BlockPlace())


def game(window: Window, level: Level = None):
	"""
	Function to run the game in a given window with a given level as the background.

	key_handler is for compatibility purposes
		:param window: The window for all graphics to be drawn on.
		:param level: The game level
	"""

	# GAME INSTANCE VARS
	key_handler: {bool} = KeyStateHandler()  # instantiate key handler
	window.push_handlers(key_handler)  # setup key handler with the window
	if level is None:
		level = Level()
	bg_music = level.music
	overlay_batch: Batch = Batch()  # batch for overlay elements
	other_labels: [Label] = [
		Label(level.name, font_name="Helvecta", font_size=35, bold=True, anchor_y='top', anchor_x='center',
		      x=window.width / 2, y=window.height, batch=overlay_batch, )]

	# -------------- SETUP -------------- #

	# creating player(s)
	for num in range(2):
		level.add(
			Player(img=resource.image(f'p_{num + 1}.png'), x=level.spawn_points[num].x, y=level.spawn_points[num].y))

	# loading of all health text for players
	for i in range(len(level.players)):
		temp_label = Label('N/A', font_name='Calibri', font_size=24, bold=True, anchor_y='top', batch=overlay_batch)
		if i % 2 is 0:
			temp_label.y = window.height - (temp_label.content_height * (i // 2))
		else:
			temp_label.anchor_x = 'right'
			temp_label.x = window.width
			temp_label.y = window.height - (temp_label.content_height * (i // 2))
		temp_label.text = str(level.players[i].starting_health)
		level.players[i].health_label = temp_label

	# play music
	if bg_music is not None:
		bg_music.play()

	# ----------------------------------- #

	@window.event
	def on_draw():
		"""
		Draws all objects to the screen.
		Called every render.
		"""
		window.clear()
		level.draw()
		overlay_batch.draw()

	@window.event
	def on_activate():
		window.maximize()

	@window.event
	def on_deactivate():
		window.minimize()

	@window.event
	def on_close():
		"""
		Performs exit actions for the game.
		Called when user closes window.
		"""
		Settings.save()

	def on_update(dt):
		"""
		Updates game with every "clock" tick.

			:param dt: Differential time between clock ticks.
		"""

		handle_keys()

		level.update(dt)
		for p in level.players:
			p.check_bounds()
			if not p.health_processed:
				p.health_label.text = str(p.health)
				color_scalar = p.starting_health / p.health
				p.health_label.color = (255, int(255 * color_scalar), int(255 * color_scalar), 255)
				p.health_processed = True

	def handle_keys():
		"""
		Reads all key inputs from the key handler and
		does the action corresponding with said key.
		"""
		# TODO: Make all control calls correspond to functions

		if key_handler["ESCAPE"]:
			Settings.global_main_window.close()

		for k in range(len(level.players)):
			if key_handler[Settings.settings[f"move_right_{k + 1}"]]:
				level.players[k].move("right")
			if key_handler[Settings.settings[f"move_left_{k + 1}"]]:
				level.players[k].move("left")

	window.set_visible(True)  # make the window visible
	clock.schedule_interval(on_update, 1 / 144)
	pyglet.app.run()  # inits pyglet and OpenGL


if __name__ == '__main__':
	main()  # main function
