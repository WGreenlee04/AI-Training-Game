import pyglet
from pyglet import clock
from pyglet import media
from pyglet import resource
from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.window import Window
from pyglet.window import key

from game.level import Level, Player
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

	# TODO: Create level here

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

	game(window=Settings.global_main_window)


def game(window: Window, level: Level = None):
	"""
	Function to run the game in a given window with a given level as the background.

	key_handler is for compatibility purposes
		:param window: The window for all graphics to be drawn on.
		:param level: The game level
	"""

	# GAME INSTANCE VARS
	key_handler: {bool} = KeyStateHandler()
	window.push_handlers(key_handler)
	if level is None:
		bg_music: media.Source = resource.media('Fluffing a Duck.wav')
	else:
		bg_music: media.Source = level.music
	main_batch: Batch = Batch()
	players: [Player] = []  # parallel with health_labels[]
	health_labels: [Label] = []  # parallel with players[]

	# -------------- SETUP -------------- #

	# creating player(s)
	players.append(Player(img=resource.image('p_red.png'), x=Player.size_x() // 2, batch=main_batch))
	players.append(Player(img=resource.image('p_blue.png'), x=window.width - Player.size_x() // 2, batch=main_batch))

	# loading of all health text to display onscreen
	for i in range(len(players)):
		temp_label = Label('N/A', font_name='Calibri', font_size=24, bold=True, anchor_y='top', batch=main_batch)
		if i % 2 is 0:
			temp_label.y = window.height - (temp_label.content_height * (i // 2))
		else:
			temp_label.anchor_x = 'right'
			temp_label.x = window.width
			temp_label.y = window.height - (temp_label.content_height * (i // 2))
		temp_label.text = str(players[i].starting_health)
		health_labels.append(temp_label)
		del temp_label

	# play music
	bg_music.play()

	# ----------------------------------- #

	@window.event
	def on_draw():
		"""
		Draws all objects to the screen.
		Called every render.
		"""
		window.clear()
		if level is not None:
			level.draw()
		main_batch.draw()

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
		# TODO: Add all exit procedures
		Settings.save()

	def on_update(dt):
		"""
		Updates game with every "clock" tick.

			:param dt: Differential time between clock ticks.
		"""

		handle_keys()

		for p, l in zip(players, health_labels):
			p.do_update(dt)
			if p.y < -p.height // 2:
				p.y = window.height + p.height // 2
			if p.x < -p.width // 2:
				p.x = window.width + p.width // 2
			elif p.x > window.width + p.width // 2:
				p.x = -p.width // 2
				if not p.health_processed:
					l.text = str(p.health)
					color_scalar = p.starting_health / p.health
					l.color = (255, int(255 * color_scalar), int(255 * color_scalar), 255)
					p.health_processed = True

	def handle_keys():
		"""
		Reads all key inputs from the key handler and
		does the action corresponding with said key.
		"""
		# TODO: Make all control calls correspond to functions

		for k in range(len(players)):
			if key_handler[Settings.settings[f"move_right_{k + 1}"]]:
				print(f"players[{k}] moved right!")
				players[k].move("right")
			if key_handler[Settings.settings[f"move_left_{k + 1}"]]:
				players[k].move("left")

	window.set_visible(True)  # make the window visible
	clock.schedule(on_update)  # calls the update function every clock tick
	pyglet.app.run()  # inits pyglet and OpenGL


if __name__ == '__main__':
	main()  # main function
