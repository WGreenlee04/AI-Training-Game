from __future__ import annotations

from builtins import function

from pyglet import media, resource
from pyglet.graphics import Batch
from pyglet.image import TextureRegion
from pyglet.sprite import Sprite
from pyglet.text import Label

from game.settings import Settings
from game.utility import Dimension, Rectangle, Vector2D, LambdaWrapper


class Collidable2D(Sprite):
    """
    Game element that has the ability to detect collision with others of its type.
    """

    def __init__(self, does_collide: bool = True, hitbox_type: str = 'image',
                 img: TextureRegion = None,
                 hitbox_coordinates: [Vector2D] = None, hitbox_dimension: Dimension = None, *args, **kwargs):
        """
        Creates a new Collidable2D object.
            :param hitbox_type: The type of hitbox to process:

                Can be one of a few types:

                'circle' - Not yet implemented

                'abstract' - Made of a coordinate array
                passed into the hitbox_coordinates argument

                'rectangle' - Made of a width and height
                passed into the hitbox_dimensions(width, height) argument.

                'image' - Made of the width and height of an image
                passed into the img argument.

                None or 'None' - No hitbox will be generated.
            :param hitbox_dimension: A tuple containing the (width, height) of the hitbox rectangle
            This is only used when the hitbox_type is 'rectangle'.
            :param img: Image or animation to display.
        """

        super(Collidable2D, self).__init__(img=img, *args, **kwargs)
        self._hitbox_type: str = hitbox_type
        self.does_collide: bool = does_collide

        if hitbox_type is None or hitbox_type.lower() == "none":
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

        if self.hitbox_type.lower() == 'image' or 'rectangle':
            return False

        if self._hitbox_type.lower() == 'abstract':
            return False


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

        self.does_update: bool = does_update
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
    _base_health: int = 100
    _base_armor: int = 10  # this is the % dmg blocked
    _base_speed: int = 216  # measured in pixels/second

    size_x: function = lambda: 80 / 1920 * int(Settings.settings["window_resolution"].split("x")[0])
    size_y: function = lambda: 80 / 1080 * int(Settings.settings["window_resolution"].split("x")[1])

    min_x: LambdaWrapper = LambdaWrapper(lambda: -Player.size_x())
    min_y: LambdaWrapper = LambdaWrapper(lambda: -Player.size_y())
    max_x: function = lambda: int(Settings.settings["window_resolution"].split("x")[0]) + Player.size_x()
    max_y: function = lambda: int(Settings.settings["window_resolution"].split("x")[1]) + Player.size_y()

    def __init__(self, health_mult: float = 1, armor_mult: float = 1, speed_mult: float = 1, img: TextureRegion = None,
                 *args, **kwargs):
        """
        Creates a new Player object.

            :param health_mult: Multiplier for health.
            :param armor_mult: Multiplier for armor.
            :param speed_mult: Multiplier for speed.
            :param img: Image or animation to display.
        """
        img.width = self.size_x()
        img.height = self.size_y()
        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2

        super(Player, self).__init__(img=img, *args, **kwargs)

        self.starting_health: int = int(self._base_health * health_mult)
        self._health: int = self.starting_health
        self.armor: int = int(self._base_armor * armor_mult)
        self.speed: int = int(self._base_speed * speed_mult)
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
        if self.x <= self.min_x():
            self.x = self.max_x()
        if self.x >= self.max_x():
            self.x = self.min_x()
        if self.y <= self.min_y():
            self.y = self.max_x()


class Level(object):
    """
    Container Class for a set of Level elements.
    """

    # TODO: Add spawn points and player count.
    def __init__(self, background: Sprite = None, collidables: [Collidable2D] = None, music: media.Source = None):
        """
        Creates a new Level.
        :param background: The Sprite that is rendered by default on the screen.
        :param collidables: List of Collidables that are rendered over the background and calculated in collisions.
        :param physical_objects: List of PhysicsObjects to be rendered a
        """
        self._batch: Batch = Batch()
        self.background: Sprite = background
        self.collidables: [Collidable2D] = collidables
        self.physical_objects: [PhysicalObject] = []
        self.players: [Player] = []
        if music is None:
            self.music: media.Source = resource.media("Fluffing a Duck.wav")
        else:
            self.music = music

        background.batch = self._batch
        for collidable in collidables:
            collidable.batch = self._batch
            if isinstance(collidable, PhysicalObject):
                self.physical_objects.append(collidable)
                if isinstance(collidable, Player):
                    self.players.append(collidable)

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
            self.background = None
            sprite.delete()
        else:
            return NotImplemented

    def draw(self):
        self._batch.draw()

    # TODO: Write level's do_update()
    def do_update(self):
        pass


# TODO: Write BlockPlace
class BlockPlace(Level):
    pass
