from __future__ import annotations

from os import walk
from pathlib import Path

from pyglet import resource
from pyglet.window import Window

from game.physics_tools import Vector2D, LambdaWrapper


class Settings:
	"""
	Container Class for instance level settings and global variables.
	Only one settings dictionary is able to be created in a game instance.
	"""

	# "GLOBAL" VARIABLES/REFERENCES #
	global_resource_path: Path = Path('resources').absolute()  # Name of settings load/save file
	global_resource_sub_folders: [str] = [x[0] for x in walk(str(global_resource_path))]
	global_main_window: Window = None  # Window for the game to render on

	# CONSTANTS #
	constant_g: LambdaWrapper = LambdaWrapper(lambda: Vector2D(0, -80 / 1080 * 2 * float(
		Settings.settings['window_resolution'].split('x')[1])))  # measured in pixels/second/second

	# SETTINGS VARS #
	file_path: str = str(Path('resources/config.txt').absolute())
	file_split: str = '='  # integral to file formatting and reading

	# SETTINGS DICT #
	settings: {str} = None  # loaded at runtime

	# DEFAULTS #
	_default_settings: {str} = {
		'move_right_1': 'D',
		'move_left_1': 'A',
		'jump_1': 'W',
		'fast_fall_1': 'S',
		'fire_right_1': 'E',
		'fire_left_1': 'Q',
		'dodge_1': 'LSHIFT',
		'move_right_2': 'NUM_6',
		'move_left_2': 'NUM_4',
		'jump_2': 'NUM_8',
		'fast_fall_2': 'NUM_5',
		'fire_right_2': 'NUM_9',
		'fire_left_2': 'NUM_7',
		'dodge_2': 'RSHIFT',
		'window_resolution': '1920x1080',
		'window_style': 'Fullscreen',
		'vsync': 'On',
	}

	@staticmethod
	def load():
		"""
		Loads the settings from the file into the Settings.settings dict.
		"""
		settings = {}
		with open(Settings.file_path, mode='r') as config_r:
			for line in config_r:
				setting = line.split(Settings.file_split, maxsplit=1)
				settings[setting[0].strip()] = setting[1].strip()
		Settings.settings = settings

	@staticmethod
	def save():
		"""
		Saves the current custom list of settings to the config file.
		"""
		with open(str(Settings.file_path), mode='w') as config_w:
			setting_names = list(Settings.settings.keys())
			setting_values = list(Settings.settings.values())
			# n is name, v is value
			for n, v in zip(setting_names, setting_values):
				config_w.write(f"{n} {Settings.file_split} {v}\n")

	@staticmethod
	def set_default(names: [] = None):
		"""
		Saves the list of default settings, effectively reverting the current settings.
		If the arguments are empty, then all config will be reset to defaults.
			:param names The list of config names to reset to their default values.
		"""
		if names is None:
			Settings.settings = Settings._default_settings
		else:
			for name in names:
				Settings.settings[name] = Settings._default_settings[name]

	@staticmethod
	def pyglet_reindex(sub_folders_add: [str] = None, sub_folders_remove: [str] = None):
		"""
		Modifies the Pyglet resource path safely.

			:param sub_folders_add: list of folder names to add.
			:param sub_folders_remove: list of folder names to remove.
		"""
		if sub_folders_add is not None:
			for folder in sub_folders_add:
				if folder not in resource.path:
					resource.path.append(str(Settings.global_resource_path.joinpath(folder)))

		if sub_folders_remove is not None:
			for folder in sub_folders_remove:
				if folder in resource.path:
					resource.path.remove(str(Settings.global_resource_path.joinpath(folder)))

		resource.reindex()
