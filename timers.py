"""
timers.py - Gestion des timers et du son CHIP-8
=================================================
Le CHIP-8 possède deux timers 8 bits décrémentés à 60 Hz :

- Delay Timer (DT) : timer général, utilisé pour synchroniser les jeux
- Sound Timer (ST) : émet un bip tant que sa valeur est > 0

Ce module gère la synchronisation à 60 Hz et la production sonore.
"""

import pygame
import numpy as np


def generate_beep(frequency=440, duration=0.1, sample_rate=44100, volume=0.3):
    """
    Génère un son de bip (onde sinusoïdale) en mémoire.

    Args:
        frequency   (int)   : fréquence du bip en Hz (440 = La standard)
        duration    (float) : durée en secondes
        sample_rate (int)   : fréquence d'échantillonnage
        volume      (float) : volume entre 0.0 et 1.0

    Returns:
        pygame.Sound: objet son prêt à être joué
    """
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)

    # Onde sinusoïdale normalisée et convertie en 16 bits signé
    wave = (np.sin(2 * np.pi * frequency * t) * volume * 32767).astype(np.int16)

    # Pygame attend un tableau stéréo (2 canaux)
    stereo_wave = np.column_stack([wave, wave])

    return pygame.sndarray.make_sound(stereo_wave)


class Timers:
    """
    Gère la synchronisation à 60 Hz et le déclenchement du son.
    """

    def __init__(self, cpu):
        """
        Initialise les timers et le système audio.

        Args:
            cpu: instance de CPU (pour accéder à sound_timer)
        """
        self.cpu = cpu

        # Initialisation de l'audio Pygame
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Génération du bip
        try:
            self.beep = generate_beep()
            self.audio_ok = True
        except Exception as e:
            print(f"[Timers] Audio non disponible : {e}")
            self.audio_ok = False

        self.beep_playing = False

    def update(self):
        """
        Décrémente les timers CPU et gère le son.
        Doit être appelé exactement 60 fois par seconde.
        """
        self.cpu.update_timers()

        # Gestion du son : joue tant que sound_timer > 0
        if self.audio_ok:
            if self.cpu.sound_timer > 0 and not self.beep_playing:
                self.beep.play(-1)       # -1 = boucle infinie
                self.beep_playing = True
            elif self.cpu.sound_timer == 0 and self.beep_playing:
                self.beep.stop()
                self.beep_playing = False
