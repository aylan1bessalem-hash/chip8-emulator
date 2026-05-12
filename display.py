"""
display.py - Affichage de l'écran CHIP-8 via Pygame

Le CHIP-8 dispose d'un écran monochrome de 64x32 pixels.
Chaque pixel est soit allumé (blanc) soit éteint (noir).

Ce module gère :
- La fenêtre Pygame
- Le tableau de pixels (64x32 booléens)
- Le dessin via toggle (XOR)
- Le rendu agrandi à l'écran (scale factor)
"""

import pygame

# Résolution native du CHIP-8
SCREEN_WIDTH  = 64
SCREEN_HEIGHT = 32

# Facteur d'agrandissement de la fenêtre (chaque pixel CHIP-8 = NxN pixels réels)
SCALE = 12

# Couleurs (R, G, B)
COLOR_OFF = (30, 30, 30)      # pixel éteint : gris très foncé
COLOR_ON  = (200, 255, 200)   # pixel allumé : vert clair (style rétro)


class Display:
    """
    Gère la fenêtre et l'affichage pixel par pixel du CHIP-8.
    """

    def __init__(self):
        """
        Initialise Pygame et crée la fenêtre de rendu.
        """
        pygame.init()

        # Taille réelle de la fenêtre (résolution native × scale)
        window_w = SCREEN_WIDTH  * SCALE
        window_h = SCREEN_HEIGHT * SCALE

        self.screen = pygame.display.set_mode((window_w, window_h))
        pygame.display.set_caption("CHIP-8 — Les Archives du Futur")

        # Tableau 2D de pixels (False = éteint, True = allumé)
        # Accès : self.pixels[x][y]
        self.pixels = [[False] * SCREEN_HEIGHT for _ in range(SCREEN_WIDTH)]

        # Flag : l'écran doit-il être redessiné ?
        self.needs_redraw = True

    def clear(self):
        """Éteint tous les pixels (opcode 00E0)."""
        self.pixels = [[False] * SCREEN_HEIGHT for _ in range(SCREEN_WIDTH)]
        self.needs_redraw = True

    def toggle_pixel(self, x, y):
        """
        Inverse l'état d'un pixel (XOR).
        Les coordonnées sont "wrappées" (le sprite déborde de l'autre côté).

        Args:
            x (int): coordonnée horizontale
            y (int): coordonnée verticale

        Returns:
            bool: True si une collision a eu lieu (pixel allumé → éteint)
        """
        # Wrap around : le sprite qui dépasse réapparaît de l'autre côté
        x = x % SCREEN_WIDTH
        y = y % SCREEN_HEIGHT

        collision = self.pixels[x][y]  # collision si le pixel était déjà allumé
        self.pixels[x][y] ^= True      # XOR : inverse l'état
        self.needs_redraw = True

        return collision

    def render(self):
        """
        Redessine la fenêtre si nécessaire.
        Chaque pixel CHIP-8 est affiché comme un carré SCALE×SCALE.
        """
        if not self.needs_redraw:
            return

        self.screen.fill(COLOR_OFF)  # fond noir

        for x in range(SCREEN_WIDTH):
            for y in range(SCREEN_HEIGHT):
                if self.pixels[x][y]:
                    rect = pygame.Rect(
                        x * SCALE,
                        y * SCALE,
                        SCALE,
                        SCALE
                    )
                    pygame.draw.rect(self.screen, COLOR_ON, rect)

        pygame.display.flip()
        self.needs_redraw = False

    def quit(self):
        """Ferme proprement Pygame."""
        pygame.quit()
