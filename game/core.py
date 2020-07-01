from __future__ import annotations

import pyglet
from pyglet import clock
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

    Settings.init()

    game(window=Settings.global_main_window)


def game(window: Window, level: Level = None):
    """
	Function to run the game in a given window with given parameters.

	key_handler is for compatibility purposes
		:param window: The window for all graphics to be drawn on.
		:param level: The game level
	"""

    # GAME INSTANCE VARS
    overlay_batch: Batch = Batch()
    key_handler: {bool} = KeyStateHandler()
    window.push_handlers(key_handler)
    if level is None:
        level: Level = Level()
    bg_music = level.music

    # -------------- SETUP -------------- #

    # creating player(s)
    for num in range(level.player_count):
        level.players.append(Player(img=resource.image(f'p_{num + 1}'), x=level.spawn_points[num].x,
                                    y=level.spawn_points[num].y, batch=overlay_batch))

    # loading of all health text to display onscreen
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
        level.do_update()

        for p in level.players:
            p.check_bounds()

    def handle_keys():
        """
		Reads all key inputs from the key handler and
		does the action corresponding with said key.
		"""
        # TODO: Make all control calls correspond to changes in player

        for k in range(len(level.players)):
            if key_handler[Settings.settings[f"move_right_{k + 1}"]]:
                pass
            if key_handler[Settings.settings[f"move_left_{k + 1}"]]:
                pass

    window.set_visible(True)  # make the window visible
    clock.schedule(on_update)  # calls the update function every clock tick
    pyglet.app.run()  # inits pyglet and OpenGL


if __name__ == '__main__':
    main()  # main function
