from __future__ import annotations

from pyglet import media, resource
from pyglet.graphics import Batch
from pyglet.image import TextureRegion
from pyglet.sprite import Sprite
from pyglet.text import Label

from game.settings import Settings
from game.utility import Dimension, Rectangle, Vector2D, GeneralUtil


class Collidable2D(Sprite):
    """
    Game element that has the ability to detect collision with others of its type.
    """

    def __init__(self, does_collide: bool = True, hitbox_type: str = 'image',
                 img: TextureRegion = None, scaled: bool = True,
                 hitbox_coordinates: [Vector2D] = None, hitbox_dimension: Dimension = None, *args, **kwargs):
        """
        Creates a new Collidable2D object.
            :param hitbox_type: The type of hitbox to process:

                Can be one of a few types:

                'circle' - Not yet implemented.

                'abstract' - Made of a coordinate array
                passed into the hitbox_coordinates argument.

                'rectangle' - Made of a width and height
                passed into the hitbox_dimensions(width, height) argument.

                'image' - Made of the width and height of an image
                passed into the img argument.

                None or 'None' - No hitbox will be generated.

            :param hitbox_dimension: A tuple containing the (width, height) of the hitbox rectangle
            This is only used when the hitbox_type is 'rectangle'.
            :param img: Image or animation to display.
        """

        if scaled:
            img.width *= 1920 / int(Settings.settings['window_resolution'].split('x')[0])
            img.height *= 1080 / int(Settings.settings['window_resolution'].split('x')[1])

        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2

        super(Collidable2D, self).__init__(img=img, *args, **kwargs)
        self._hitbox_type: str = hitbox_type
        self.does_collide: bool = does_collide

        if hitbox_type is None or hitbox_type.lower() == 'none':
            pass
        elif hitbox_type.lower() == 'image':
            if img.width and img.height != 0:
                self._hitbox = Rectangle(img.width, img.height)
            else:
                self._hitbox = Rectangle(img.get_texture(True).width, img.get_texture(True).height)
        elif hitbox_type.lower() == 'rectangle':
            self._hitbox = Rectangle(hitbox_dimension.width, hitbox_dimension.height)
        elif hitbox_type.lower() == 'abstract':
            self._hitbox = hitbox_coordinates

    def is_colliding(self, other: Collidable2D) -> bool:
        """
        Checks if the hitboxes of this object and another are overlapping.
        :param other: The other Collidable2D to be checked.
        :return: Boolean value of collision.
        """

        if not self.does_collide or self._hitbox_type is None or self._hitbox_type.lower() == 'none':
            return False

        return False

        # if self.hitbox_type.lower() == 'image' or self.hitbox_type.lower() == 'rectangle':
        #   return False

        # if self._hitbox_type.lower() == 'abstract':
        #   return False


class PhysicalObject(Collidable2D):
    """
    Game element that has the ability to obey game physics.
    """
    _base_mass: float = 1  # measured in standard masses

    def __init__(self, does_update=True, mass_mult=1, *args, **kwargs):
        """
        Creates a new PhysicalObject object.
        :param does_update: If the physics update is run on this object.
        :param mass_mult: Multiplier for the mass of the object.
        :param img: Image or animation to display.
        """
        super(PhysicalObject, self).__init__(*args, **kwargs)

        self.does_update: bool = does_update  # if the do_update function runs
        self.mass: float = self._base_mass * mass_mult
        self.dx: Vector2D = Vector2D()  # velocity

    def do_update(self, dt):
        if self.does_update:
            self.x += self.dx.x * dt
            self.y += self.dx.y * dt

    def apply_force(self, force: Vector2D):
        self.dx += force / self.mass


class Player(PhysicalObject):
    """
    Human/AI controlled element for gameplay.

    Has physics and collision.
    """
    # Player Class Attributes
    _base_health: int = 100  # no units
    _base_armor: int = 10  # this is the % dmg blocked (max 100
    _base_speed: () = lambda: 600 / 1080 * int(
        Settings.settings['window_resolution'].split('x')[1])  # measured in pixels/second

    standard_width: () = lambda: 80 / 1920 * int(Settings.settings['window_resolution'].split('x')[0])
    standard_height: () = lambda: 80 / 1080 * int(Settings.settings['window_resolution'].split('x')[1])

    min_x: () = lambda: -Player.standard_width()
    min_y: () = lambda: -Player.standard_height()
    max_x: () = lambda: int(Settings.settings['window_resolution'].split('x')[0]) + Player.standard_width()
    max_y: () = lambda: int(Settings.settings['window_resolution'].split('x')[1]) + Player.standard_height()

    def __init__(self, health_mult: float = 1, armor_mult: float = 1, speed_mult: float = 1, img: TextureRegion = None,
                 *args, **kwargs):
        """
        Creates a new Player object.

            :param health_mult: Multiplier for health.
            :param armor_mult: Multiplier for armor.
            :param speed_mult: Multiplier for speed.
            :param img: Image or animation to display.
        """
        img.width = Player.standard_width()
        img.height = Player.standard_height()
        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2

        super(Player, self).__init__(img=img, scaled=False, *args, **kwargs)

        self.starting_health: int = int(self._base_health * health_mult)
        self._health: int = self.starting_health
        self.armor: int = int(self._base_armor * armor_mult)
        self.speed: int = int(Player._base_speed() * speed_mult)
        self.health_label: Label = Label()
        self.health_processed: bool = True

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, health: int):
        """
        Uses armor to properly calculate health changes.
        :param health: Amount of health to change by.
        """
        if health <= 0:
            health *= (1 - self.armor)
        self._health += int(health)
        self.health_processed = False

    def do_update(self, dt):
        super(Player, self).do_update(dt=dt)
        if not self.health_processed:
            self.health_label.text = str(self.health)
            color_scalar = self.starting_health / self.health
            self.health_label.color = (255, int(255 * color_scalar), int(255 * color_scalar), 255)
            self.health_processed = True

    def check_bounds(self):
        if self.x < Player.min_x():
            self.x = Player.max_x()
        if self.x > Player.max_x():
            self.x = Player.min_x()
        if self.y < Player.min_y():
            self.y = Player.max_y()


class Level(object):
    """
    Container Class for a set of Level elements.
    """

    def __init__(self, background: Sprite = None, objects: [Collidable2D] = None, music: media.Source = None,
                 name: str = None, spawn_points: [Vector2D] = None):
        """
        Creates a new Level.
            :param background: The background Sprite.
            :param objects: All objects in the level.
            :param music: Sounds to be played in the background while game is running.
            :param name: Name to be displayed for the level
            :param spawn_points: Places for players to spawn into the level
        """
        self._batch: Batch = Batch()
        self.background: Sprite = background
        self.collidables: [Collidable2D] = []
        self.physical_objects: [PhysicalObject] = []
        self.players: [Player] = []
        if objects is not None:
            self.collidables.append(*objects)
        if music is None:
            self.music: media.Source = resource.media('Fluffing a Duck.wav')
        else:
            self.music: media.Source = music
        if name is None:
            self.name: str = 'Default Level'
        else:
            self.name: str = name

        if spawn_points is not None:
            self.spawn_points = spawn_points
            self.max_players = len(spawn_points)
        else:
            self.spawn_points = [Vector2D(Settings.global_main_window.width // 5, 100),
                                 Vector2D(Settings.global_main_window.width * 4 // 5, 100)]
            self.max_players = 2

        # ADDING BATCHES AND SORTING OBJECTS #
        if background is not None:
            background.batch = self._batch
        if objects is not None:
            for obj in objects:
                obj.batch = self._batch
                if isinstance(obj, PhysicalObject):
                    self.physical_objects.append(obj)
                    if isinstance(obj, Player):
                        self.players.append(obj)

    def add(self, sprite: Sprite):
        """
        Adds a Sprite to the level to be calculated in the gamespace.
        :param sprite: The Sprite to be added
        :return: NotImplemented if type is not supported.
        """
        if isinstance(sprite, Collidable2D):
            sprite.batch = self._batch
            self.collidables.append(sprite)
            if isinstance(sprite, PhysicalObject):
                self.physical_objects.append(sprite)
                if isinstance(sprite, Player):
                    self.players.append(sprite)
        elif isinstance(sprite, Sprite):
            sprite.batch = self._batch
            self.background = sprite
        else:
            return NotImplemented

    def remove(self, sprite: Sprite):
        """
        Remove a Sprite from the gamespace.
        :param sprite: The Sprite to be removed.
        :return: NotImplemented if the type is not Supported
        """

        if isinstance(sprite, Collidable2D):
            self.collidables.remove(sprite)
            if isinstance(sprite, PhysicalObject):
                self.physical_objects.remove(sprite)
                if isinstance(sprite, Player):
                    self.players.remove(sprite)
            sprite.delete()
        elif isinstance(sprite, Sprite):
            if sprite is self.background:
                self.background = None
                sprite.delete()
        else:
            return NotImplemented

    def draw(self):
        self._batch.draw()

    def do_update(self, dt):
        for obj in self.physical_objects:
            obj.apply_force(Settings.constant_g() * dt)
            collides = False
            for col_obj in self.collidables:
                if obj.is_colliding(col_obj):
                    collides = True
            if not collides:
                obj.do_update(dt=dt)


class BlockPlace(Level):

    def __init__(self):
        main_platforms: [Collidable2D] = [Collidable2D(hitbox_type='image', img=GeneralUtil.loadResizedImage(
            resource.image('default_platform.png'), 1400, 400),
                                                       x=Settings.global_main_window.width // 2,
                                                       y=Settings.global_main_window.height // 3)]
        spawn_points = []
        for main_platform in main_platforms:
            main_platform.anchor_x = main_platform.width / 2
            main_platform.anchor_y = main_platform.height / 2
            spawn_points.append(Vector2D(
                main_platform.x - (main_platform.width / 2 - Player.standard_width() / 2),
                main_platform.y + main_platform.height / 2 + Player.standard_height() / 2))
            spawn_points.append(
                Vector2D(main_platform.x + (main_platform.width / 2 - Player.standard_width() / 2),
                         main_platform.y + main_platform.height / 2 + Player.standard_height() / 2))

        super(BlockPlace, self).__init__(objects=main_platforms, name="Block Place",
                                         music=resource.media("Fluffing a Duck.wav"), spawn_points=spawn_points)
