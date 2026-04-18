"""
keyboard.py - Gestion du clavier CHIP-8
=========================================
Le CHIP-8 possède un clavier hexadécimal de 16 touches (0x0 à 0xF).
Disposition originale :
    1 2 3 C
    4 5 6 D
    7 8 9 E
    A 0 B F

Mapping vers le clavier AZERTY / QWERTY moderne :
    1 2 3 4
    Q W E R
    A S D F
    Z X C V

Ce module gère :
- Le mapping CHIP-8 ↔ touches physiques
- L'état pressé/relâché de chaque touche
- La récupération de la dernière touche pressée
"""

import pygame

# Mapping : touche CHIP-8 (0x0..0xF) → touche Pygame
# Adapté pour un clavier AZERTY/QWERTY
KEYMAP = {
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_4: 0xC,

    pygame.K_q: 0x4,
    pygame.K_w: 0x5,
    pygame.K_e: 0x6,
    pygame.K_r: 0xD,

    pygame.K_a: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_f: 0xE,

    pygame.K_z: 0xA,
    pygame.K_x: 0x0,
    pygame.K_c: 0xB,
    pygame.K_v: 0xF,
}


class Keyboard:
    """
    Gère l'état des 16 touches du clavier CHIP-8.
    """

    def __init__(self):
        """
        Initialise le tableau d'état des touches (toutes relâchées).
        """
        # 16 touches : False = relâchée, True = pressée
        self.keys = [False] * 16

        # Dernière touche pressée (pour l'instruction FX0A)
        self._last_pressed = None

    def handle_event(self, event):
        """
        Met à jour l'état des touches en fonction des événements Pygame.

        Args:
            event (pygame.event.Event): événement clavier
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEYMAP:
                chip8_key = KEYMAP[event.key]
                self.keys[chip8_key] = True
                self._last_pressed = chip8_key

        elif event.type == pygame.KEYUP:
            if event.key in KEYMAP:
                chip8_key = KEYMAP[event.key]
                self.keys[chip8_key] = False

    def is_key_pressed(self, key):
        """
        Vérifie si une touche CHIP-8 est actuellement pressée.

        Args:
            key (int): numéro de touche CHIP-8 (0x0 à 0xF)

        Returns:
            bool: True si pressée
        """
        return self.keys[key]

    def get_pressed_key(self):
        """
        Retourne la dernière touche pressée puis réinitialise le buffer.
        Utilisé par l'instruction FX0A (attente d'une touche).

        Returns:
            int | None: numéro de touche CHIP-8, ou None si aucune
        """
        key = self._last_pressed
        self._last_pressed = None
        return key
