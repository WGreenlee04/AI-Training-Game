from pathlib import Path

import pygame


# main function
def main():
	# initialize pygame
	pygame.init()
	# load logo
	logo_path = Path("resources/sprites/logo320x320.png")
	logo = pygame.image.load(str(logo_path))  # logo has the type 'surface' which is like an image
	# congfigure display window
	pygame.display.set_icon(logo)
	pygame.display.set_caption("ShooterGame")

	# use current flags (set above) to render window
	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

	running = True

	while running:
		# for each event in the event queue
		for event in pygame.event.get():
			# event handler
			if event.type == pygame.QUIT:
				running = False

	pygame.quit()
