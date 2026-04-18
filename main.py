"""
main.py - Point d'entrée de l'interpréteur CHIP-8
===================================================
Ce fichier orchestre tous les modules et lance la boucle principale.

Utilisation :
    python main.py <chemin_vers_la_rom>

Exemple :
    python main.py roms/pong.ch8

La boucle principale gère :
- La cadence d'exécution (500 Hz pour les instructions CPU)
- La cadence des timers (60 Hz)
- Les événements clavier
- Le rendu à l'écran
"""

import sys
import time
import pygame 

from cpu      import CPU
from display  import Display
from keyboard import Keyboard
from timers   import Timers


# ---------------------------------------------------------------------------
# Paramètres de vitesse
# ---------------------------------------------------------------------------

CPU_HZ    = 500   # Nombre d'instructions exécutées par seconde
TIMER_HZ  = 60    # Fréquence de décrémentation des timers (standard CHIP-8)


def main():
    """
    Fonction principale : initialise les composants et lance la boucle.
    """

    # Vérification des arguments
    if len(sys.argv) < 2:
        print("Usage : python main.py <chemin_vers_la_rom>")
        print("Exemple : python main.py roms/pong.ch8")
        sys.exit(1)

    rom_path = sys.argv[1]

    # --- Initialisation des composants ---
    display  = Display()
    keyboard = Keyboard()
    cpu      = CPU(display, keyboard)
    timers   = Timers(cpu)

    # Chargement de la ROM
    try:
        cpu.load_rom(rom_path)
    except FileNotFoundError:
        print(f"[Erreur] Fichier ROM introuvable : {rom_path}")
        sys.exit(1)

    print("[Main] Démarrage de l'émulateur...")
    print("       Appuyez sur ECHAP pour quitter.")

    # --- Calcul des intervalles de temps ---
    cpu_interval   = 1.0 / CPU_HZ     # ~0.002 s entre chaque instruction
    timer_interval = 1.0 / TIMER_HZ   # ~0.0167 s entre chaque tick timer

    last_cpu_time   = time.time()
    last_timer_time = time.time()

    # --- Boucle principale ---
    running = True
    while running:

        now = time.time()

        # Traitement des événements Pygame (clavier, fermeture de fenêtre)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                keyboard.handle_event(event)

            elif event.type == pygame.KEYUP:
                keyboard.handle_event(event)

        # Exécution des cycles CPU à la fréquence cible
        if now - last_cpu_time >= cpu_interval:
            cpu.cycle()
            last_cpu_time = now

        # Mise à jour des timers à 60 Hz
        if now - last_timer_time >= timer_interval:
            timers.update()
            last_timer_time = now

        # Rendu de l'écran (seulement si des pixels ont changé)
        display.render()

        # Petite pause pour ne pas saturer le CPU de l'ordinateur
        time.sleep(0.0001)

    # --- Fermeture propre ---
    print("[Main] Fermeture de l'émulateur.")
    display.quit()


if __name__ == "__main__":
    main()
