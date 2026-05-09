 CHIP-8 Emulator

Nous avons fait un émulateur CHIP-8 en Python. Il permet de jouer à des vieux jeux comme Space Invaders.

Ce qu'il faut pour l'installer

- Python 3.12 (pas la 3.14, ça marche pas avec pygame)
- Un ordinateur avec Windows

Comment installer

1. **Téléchargez tous les fichiers** et mettez-les dans un dossier.

2. **Ouvrez PowerShell** dans ce dossier.

3. Installez Pygame et NumPy :
 pip install pygame numpy
  Si ça ne marche pas, essayez :
  py -m pip install pygame numpy


Comment lancer un jeu

1. **Mettez votre ROM** (fichier `.ch8`) dans le dossier `roms`.

2. **Lancez l'émulateur** :

   py -3.12 main.py roms/ma_rom.ch8



   
-Les touches

| CHIP-8 | Clavier |
|--------|---------|
| 1 2 3 C | 1 2 3 4 |
| 4 5 6 D | Q W E R |
| 7 8 9 E | A S D F |
| A 0 B F | Z X C V |

ECHAP = quitter

- Dépannage

| Problème | Solution |
|----------|----------|
| pip non trouvé | `py -m pip install pygame numpy` |
| Python 3.14 | Utilisez `py -3.12` au lieu de `python` |

- Les fichiers

- `cpu.py` : le cerveau (mémoire, instructions)
- `display.py` : l'écran
- `keyboard.py` : le clavier
- `timers.py` : le son
- `main.py` : lance tout

  




