from __future__ import annotations

from pyglet import media, resource
from pyglet.graphics import Batch
from pyglet.image import TextureRegion
from pyglet.sprite import Sprite
from pyglet.text import Label

from game.physics_tools import Dimension, Rectangle, Vector2D, LambdaWrapper
from game.settings import Settings


# TODO: Make collision based on https://www.metanetsoftware.com/technique/tutorialA.html#section0
class Collidable2D(Sprite):
	"""
	Game element that has the ability to detect collision with others of its type.
	"""

	def __init__(self, hitbox_type: str = 'image', hitbox_dimension: Dimension = None,
	             img: TextureRegion = None, scaled: bool = True, *args, **kwargs):
		"""
		:param hitbox_type: The type of hitbox to process:

			Can be one of a few types:

			'circle' - Not yet implemented.

			'rectangle' - Made of a width and height
				passed into the dimensions(width, height) argument.

			'image' - Made of the width and height of an image
				passed into the img argument.

			None or 'None' - No hitbox will be generated.

		:param hitbox_dimension: A tuple containing the (width, height) of the hitbox rectangle.
			This is only used when the hitbox_type is 'rectangle'.
		:param img: Image or animation to display.
		"""

		# Set anchoring
		img.anchor_x = img.width / 2
		img.anchor_y = img.height / 2

		super(Collidable2D, self).__init__(img=img, *args, **kwargs)

		# Scale the object to screen size
		if scaled:
			self.scale = 1920 / Settings.global_main_window.width

		self.hitbox_type: str = hitbox_type

		if hitbox_type in [None, 'None']:
			pass
		elif hitbox_type == 'image':
			if img.width and img.height != 0:
				self.hitbox = Rectangle(img.width, img.height)
			else:
				self.hitbox = Rectangle(img.get_texture(True).width, img.get_texture(True).height)
		elif hitbox_type == 'rectangle':
			self.hitbox = Rectangle(hitbox_dimension.width, hitbox_dimension.height)

	def is_colliding(self, other: Collidable2D) -> bool:
		"""
		Checks if the hitboxes of this object and another are overlapping.
		:param other: The other Collidable2D to be checked.
		:return: Boolean value of collision.
		"""

		# gets the absolute coordinates of
		# l1 - top left of self
		# r1 - bottom right of self
		# l2 - top left of other
		# r2 - bottom right of other
		x, y, ox, oy = self.x, self.y, other.x, other.y
		l1 = self.hitbox.coordinates.tl
		r1 = self.hitbox.coordinates.br
		l2 = other.hitbox.coordinates.tl
		r2 = other.hitbox.coordinates.br

		if self.hitbox_type and other.hitbox_type is not None:
			l1 = Vector2D.Point(l1.x + x, l1.y + y)
			r1 = Vector2D.Point(r1.x + x, r1.y + y)
			l2 = Vector2D.Point(l2.x + ox, l1.y + oy)
			r2 = Vector2D.Point(r2.x + ox, r1.y + oy)

		# if they are left or right of each other
		if l1.x >= r2.x or l2.x >= r1.x:
			return False

		# if they are above or below each other
		if l1.y <= r2.y or l2.y <= r1.y:
			return False

		return True


class PhysicalObject(Collidable2D):
	"""
	Game element that has the ability to obey game physics.
	"""
	_base_mass: float = 1  # measured in standard masses

	def __init__(self, does_update=True, mass_mult=1, *args, **kwargs):
		"""
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
			self.dx += Settings.constant_g() * dt
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
	_base_speed: int = 300  # measured in pixels/second

	standard_width: LambdaWrapper = LambdaWrapper(
		lambda: 80 / 1920 * int(Settings.settings['window_resolution'].split('x')[0]))
	standard_height: LambdaWrapper = LambdaWrapper(
		lambda: 80 / 1080 * int(Settings.settings['window_resolution'].split('x')[1]))

	min_y: LambdaWrapper = LambdaWrapper(lambda: -Player.standard_height() // 2)
	max_y: LambdaWrapper = LambdaWrapper(lambda: Settings.global_main_window.height + Player.standard_height() // 2)
	min_x: LambdaWrapper = LambdaWrapper(lambda: -Player.standard_width() // 2)
	max_x: LambdaWrapper = LambdaWrapper(lambda: Settings.global_main_window.width + Player.standard_width() // 2)

	def __init__(self, health_mult: float = 1, armor_mult: float = 1, speed_mult: float = 1, img: TextureRegion = None,
	             *args, **kwargs):
		"""
			:param health_mult: Multiplier for health.
			:param armor_mult: Multiplier for armor.
			:param speed_mult: Multiplier for speed.
			:param img: Image or animation to display.
		"""
		img.width = self.standard_width()
		img.height = self.standard_height()

		super(Player, self).__init__(img=img, scaled=False, *args, **kwargs)

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
		self.health_processed = True

	def move(self, arg: str):
		"""
		Built in method to calculate movement of a Player.
		:param arg: Direction of movement.
		:return:
		"""
		if arg.lower() == 'left':
			if self.dx.x > -self.speed:
				self.apply_force(Vector2D(-self.speed, 0))
		if arg.lower() == 'right':
			if self.dx.x < self.speed:
				self.apply_force(Vector2D(self.speed, 0))

	def check_bounds(self):
		if self.y < Player.min_y():
			self.y = Player.max_y()
		if self.x < Player.min_x():
			self.x = Player.max_x()
		elif self.x > Player.max_x():
			self.x = Player.min_x()


class Level(object):
	"""
	Container Class for a set of Level elements.
	"""

	def __init__(self, background: Sprite = None, objects: [Collidable2D] = None, music: media.Source = None,
	             name: str = 'None', spawn_points: [Vector2D.Point] = None):
		"""
		:param background: The background Sprite.
		:param objects: All objects in the level.
		:param music: Sounds to be played in the background while game is running.
		:param name: Name to be displayed for the level
		:param spawn_points: Places for players to spawn into the level
		"""

		self._background: Sprite = background
		if objects is not None:
			self._objects: [Collidable2D] = objects
		else:
			self._objects: [Collidable2D] = []
		self.players: [Player] = []  # all players in the level
		self._batch: Batch = Batch()  # graphics batch
		self.music: media.Source = music  # music to be played in background
		self.name = name  # name of the level
		if spawn_points is not None:
			self.spawn_points = spawn_points
			self.max_players = len(spawn_points)
		else:
			self.spawn_points = [Vector2D.Point(Settings.global_main_window.width // 5, 100),
			                     Vector2D.Point(Settings.global_main_window.width * 4 // 5)]
			self.max_players = 2

		# BATCH SETUP #
		if background is not None:
			background.batch = self._batch
		for obj in self._objects:
			obj.batch = self._batch
			if isinstance(obj, Player):
				self.players.append(obj)

	def add(self, sprite: Sprite):
		"""
		Adds a Sprite to the level to be calculated in the gamespace.
		:param sprite: The Sprite to be added
		:return: NotImplemented if type is not supported.
		"""
		sprite.batch = self._batch
		if isinstance(sprite, Collidable2D):
			self._objects.append(sprite)
			if isinstance(sprite, Player):
				self.players.append(sprite)
		elif isinstance(sprite, Sprite):
			self._background = sprite
		else:
			return NotImplemented

	def remove(self, sprite: Sprite):
		"""
		Remove a Sprite from the gamespace.
		:param sprite: The Sprite to be removed.
		:return: NotImplemented if the type is not Supported
		"""
		sprite.batch = None
		if isinstance(sprite, Collidable2D):
			self._objects.remove(sprite)
			if isinstance(sprite, Player):
				self.players.remove(sprite)
		elif isinstance(sprite, Sprite):
			if sprite is self._background:
				self._background = None
		else:
			return NotImplemented

	def draw(self):
		self._batch.draw()

	def update(self, dt):
		for obj in self._objects:
			if isinstance(obj, PhysicalObject):
				for col_obj in self._objects:
					if not obj.is_colliding(col_obj):
						obj.do_update(dt)


class BlockPlace(Level):

	def __init__(self):
		main_platforms: [Collidable2D] = [Collidable2D(hitbox_type='image', img=resource.image('default_platform.png'),
		                                               x=Settings.global_main_window.width // 2,
		                                               y=Settings.global_main_window.height // 3)]
		spawn_points = []
		for main_platform in main_platforms:
			main_platform.anchor_x = main_platform.width / 2
			main_platform.anchor_y = main_platform.height / 2
			spawn_points.append(Vector2D.Point(
				main_platform.x - (main_platform.width / 2 - Player.standard_width() / 2),
				main_platform.y + main_platform.height / 2 + Player.standard_height() / 2))
			spawn_points.append(
				Vector2D.Point(main_platform.x + (main_platform.width / 2 - Player.standard_width() / 2),
				               main_platform.y + main_platform.height / 2 + Player.standard_height() / 2))

		super(BlockPlace, self).__init__(objects=main_platforms, name="Block Place",
		                                 music=resource.media("Fluffing a Duck.wav"), spawn_points=spawn_points)
