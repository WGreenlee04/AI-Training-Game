from __future__ import annotations

import pyglet
from pyglet import clock
from pyglet import resource
from pyglet.graphics import Batch
from pyglet.text import Label
from pyglet.window import Window, key

from game.level import Level, BlockPlace, Player
from game.settings import Settings
from game.utility import Vector2D


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
    level = BlockPlace()
    players = []
    for num in range(2):
        players.append(
            Player(img=resource.image(f'p_{num + 1}.png'), x=level.spawn_points[num].x, y=level.spawn_points[num].y))
    game_local(window=Settings.global_main_window, level=level, players=players)


def game_local(window: Window, level: Level = None, players: [Player] = None):
    """
    Function to run the game in a given window with given parameters.

    key_handler is for compatibility purposes
        :param window: The window for all graphics to be drawn on.
        :param level: The game level
        :param players: The players to be calculated in gameplay.
    """

    # GAME INSTANCE VARS
    overlay_batch: Batch = Batch()  # The graphics batch of the overlay in this game instance
    key_handler: {bool} = KeyStateHandler()  # The key listener equivalent for this game
    window.push_handlers(key_handler)  # Tell it which window to listen to
    if level is None:
        level: Level = Level()  # Default level
    other_labels: [Label] = [
        Label(level.name, font_name='Helvecta', font_size=35, bold=True, anchor_y='top', anchor_x='center',
              x=window.width / 2, y=window.height, batch=overlay_batch, )]  # name of the level

    # -------------- SETUP -------------- #

    if players is not None:
        for player in players:
            level.add(player)

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
        level.do_update(dt=dt)

        for p in level.players:
            p.check_bounds()

    def handle_keys():
        """
        Reads all key inputs from the key handler and
        does the action corresponding with said key.
        """
        # TODO: Make all control calls correspond to changes in player

        for k in range(len(level.players)):
            controlled_player = level.players[k]
            if key_handler[Settings.settings[f'move_right_{k + 1}']]:
                if controlled_player.dx.x < controlled_player.speed:
                    controlled_player.apply_force(Vector2D(controlled_player.speed, 0))
            if key_handler[Settings.settings[f'move_left_{k + 1}']]:
                if controlled_player.dx.x > -controlled_player.speed:
                    controlled_player.apply_force(Vector2D(-controlled_player.speed, 0))

    window.set_visible(True)  # make the window visible
    clock.schedule(on_update)  # calls the update function every clock tick
    if level.music is not None:
        level.music.play()  # background music
    pyglet.app.run()  # inits pyglet and OpenGL


if __name__ == '__main__':
    main()  # main function
