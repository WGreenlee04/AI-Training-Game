# -*- coding: utf8 -*-

__author__ = "Sven Hecht"
__license__ = "GPL"
__version__ = "1.0.2"
__maintainer__ = "William Greenlee"
__email__ = "greenlee04@gmail.com"
__status__ = "Production"

from collections import namedtuple
from math import *
from random import *


class Vector2D(object):
	"""
	Class that acts as a mathematical 2D vector for physics calculations.
	"""

	def __init__(self, x=0, y=0):
		self.x = 0
		self.y = 0
		if isinstance(x, tuple) or isinstance(x, list):
			y = x[1]
			x = x[0]
		elif isinstance(x, Vector2D):
			y = x.y
			x = x.x

		self.set(x, y)

	@staticmethod
	def random(size=1):
		sizex = size
		sizey = size
		if isinstance(size, tuple) or isinstance(size, list):
			sizex = size[0]
			sizey = size[1]
		elif isinstance(size, Vector2D):
			sizex = size.x
			sizey = size.y
		return Vector2D(random() * sizex, random() * sizey)

	@staticmethod
	def random_unit_circle():
		d = random() * pi
		return Vector2D(cos(d) * choice([1, -1]), sin(d) * choice([1, -1]))

	@staticmethod
	def distance(a, b):
		return (a - b).get_length()

	@staticmethod
	def angle(v1, v2):
		return acos(v1.dot_product(v2) / (v1.get_length() * v2.get_length()))

	@staticmethod
	def angle_deg(v1, v2):
		return Vector2D.angle(v1, v2) * 180.0 / pi

	def set(self, x, y):
		self.x = x
		self.y = y

	def to_arr(self):
		return [self.x, self.y]

	def to_int(self):
		return Vector2D(int(self.x), int(self.y))

	def to_int_arr(self):
		return self.to_int().to_arr()

	def get_normalized(self):
		if self.get_length() != 0:
			return self / self.get_length()
		else:
			return Vector2D(0, 0)

	def dot_product(self, other):
		if isinstance(other, Vector2D):
			return self.x * other.x + self.y * other.y
		elif isinstance(other, tuple) or isinstance(other, list):
			return self.x * other[0] + self.y * other[1]
		else:
			return NotImplemented

	def __add__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x + other.x, self.y + other.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(self.x + other[0], self.y + other[1])
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x + other, self.y + other)
		else:
			return NotImplemented

	def __sub__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x - other.x, self.y - other.y)
		if isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(self.x - other[0], self.y - other[1])
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x - other, self.y - other)
		else:
			return NotImplemented

	def __rsub__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(other.x - self.x, other.y - self.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(other[0] - self.x, other[1] - self.y)
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(other - self.x, other - self.y)
		else:
			return NotImplemented

	def __mul__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x * other.x, self.y * other.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(self.x * other[0], self.y * other[1])
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x * other, self.y * other)
		else:
			return NotImplemented

	def __floordiv__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x // other.x, self.y // other.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(self.x // other[0], self.y // other[1])
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x // other, self.y // other)
		else:
			return NotImplemented

	def __truediv__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x / other.x, self.y / other.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(self.x / other[0], self.y / other[1])
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x / other, self.y / other)
		else:
			return NotImplemented

	def __rdiv__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(other.x / self.x, other.y / self.y)
		elif isinstance(other, tuple) or isinstance(other, list):
			return Vector2D(other[0] / self.x, other[1] / self.y)
		elif isinstance(other, int) or isinstance(other, float):
			return Vector2D(other / self.x, other / self.y)
		else:
			return NotImplemented

	def __pow__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			return Vector2D(self.x ** other, self.y ** other)
		else:
			return NotImplemented

	def __iadd__(self, other):
		if isinstance(other, Vector2D):
			self.x += other.x
			self.y += other.y
			return self
		elif isinstance(other, tuple) or isinstance(other, list):
			self.x += other[0]
			self.y += other[1]
			return self
		elif isinstance(other, int) or isinstance(other, float):
			self.x += other
			self.y += other
			return self
		else:
			return NotImplemented

	def __isub__(self, other):
		if isinstance(other, Vector2D):
			self.x -= other.x
			self.y -= other.y
			return self
		elif isinstance(other, tuple) or isinstance(other, list):
			self.x -= other[0]
			self.y -= other[1]
			return self
		elif isinstance(other, int) or isinstance(other, float):
			self.x -= other
			self.y -= other
			return self
		else:
			return NotImplemented

	def __imul__(self, other):
		if isinstance(other, Vector2D):
			self.x *= other.x
			self.y *= other.y
			return self
		elif isinstance(other, tuple) or isinstance(other, list):
			self.x *= other[0]
			self.y *= other[1]
			return self
		elif isinstance(other, int) or isinstance(other, float):
			self.x *= other
			self.y *= other
			return self
		else:
			return NotImplemented

	def __idiv__(self, other):
		if isinstance(other, Vector2D):
			self.x /= other.x
			self.y /= other.y
			return self
		elif isinstance(other, tuple) or isinstance(other, list):
			self.x /= other[0]
			self.y /= other[1]
			return self
		elif isinstance(other, int) or isinstance(other, float):
			self.x /= other
			self.y /= other
			return self
		else:
			return NotImplemented

	def __ipow__(self, other):
		if isinstance(other, int) or isinstance(other, float):
			self.x **= other
			self.y **= other
			return self
		else:
			return NotImplemented

	def __eq__(self, other):
		if isinstance(other, Vector2D):
			return self.x == other.x and self.y == other.y
		else:
			return NotImplemented

	def __ne__(self, other):
		if isinstance(other, Vector2D):
			return self.x != other.x or self.y != other.y
		else:
			return NotImplemented

	def __gt__(self, other):
		if isinstance(other, Vector2D):
			return self.get_length() > other.get_length()
		else:
			return NotImplemented

	def __ge__(self, other):
		if isinstance(other, Vector2D):
			return self.get_length() >= other.get_length()
		else:
			return NotImplemented

	def __lt__(self, other):
		if isinstance(other, Vector2D):
			return self.get_length() < other.get_length()
		else:
			return NotImplemented

	def __le__(self, other):
		if isinstance(other, Vector2D):
			return self.get_length() <= other.get_length()
		else:
			return NotImplemented

	def __len__(self):
		return int(sqrt(self.x ** 2 + self.y ** 2))

	def get_length(self):
		return sqrt(self.x ** 2 + self.y ** 2)

	def __getitem__(self, key):
		if key in ['x', 'X', 0, '0']:
			return self.x
		elif key in ['y', 'Y', 1, '1']:
			return self.y

	def __str__(self):
		return f"[x: {self.x}, y: {self.y}]"

	def __repr__(self):
		return f"{'x': {self.x}, 'y': {self.y}}"

	def __neg__(self):
		return Vector2D(-self.x, -self.y)


class Dimension(object):
	"""
	Class that holds a width and height of an item.
	"""

	def __init__(self, width, height):
		self.width = width
		self.height = height

	def __eq__(self, other):
		if isinstance(other, Dimension):
			return self.height == other.width and self.width == other.width
		else:
			return NotImplemented

	@property
	def area(self):
		"""
		The space occupied by the Dimension.
			:return: The area of the Dimension.
		"""
		return self.height * self.width


class Rectangle(Dimension):
	"""
	Class that holds the width and height of a rectangle,
	as well as the top left and bottom right coordinate of that
	same rectangle.
	"""
	Point: namedtuple = namedtuple('Point', ['x', 'y'])
	Coordinates: namedtuple = namedtuple('Coordinates', ['tl', 'br'])

	@property
	def bounds(self) -> Dimension:
		"""
		The dimensions of the rectangle.
			:return: The Dimension of the bounds of the rectangle.
		"""
		return Dimension(self.width, self.height)

	@property
	def coordinates(self) -> Coordinates:
		"""
		The top left and bottom right coordinates of the rectangle.
			:return: Coordinates of the rectangle as namedtuple(tl, br)
		"""
		half_width = self.width // 2
		half_height = self.height // 2
		return self.Coordinates(self.Point(-half_width, half_height), self.Point(half_width, -half_height))

	@bounds.setter
	def bounds(self, bounds: Dimension):
		"""
		Sets the width and height of the rectangle through a dimension.
			:param bounds: The dimension to be followed
		"""
		self.width = bounds.width
		self.height = bounds.height

	@coordinates.setter
	def coordinates(self, coordinates: Coordinates):
		"""
		Sets the coordinates of the top left and bottom right of the rectangle.
			:param coordinates: Coordinates in the form Coordinates(tl: Point(x,y), br: Point(x,y))
		"""
		self.width = abs(coordinates[0][0]) + abs(coordinates[1][0])
		self.height = abs(coordinates[0][1]) + abs(coordinates[1][1])


class LambdaWrapper(object):
	"""
	Makes Lambda items (callable vars) more efficient.
	"""

	def __init__(self, func):
		self.func = func
		self.value = None

	def __call__(self):
		if self.value is None:
			self.value = self.func()
		return self.value
