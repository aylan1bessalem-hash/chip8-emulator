"""
cpu.py - Coeur de l'interpréteur CHIP-8
========================================
Ce module gère :
- La mémoire (4096 octets)
- Les 16 registres généraux (V0 à VF)
- Le registre d'adresse (I)
- Le compteur de programme (PC)
- La pile (stack) et le pointeur de pile (SP)
- Le décodage et l'exécution de tous les opcodes CHIP-8
"""

import random



# Polices de caractères intégrées (sprites 4x5 pixels pour les chiffres 0-F)
# Chaque caractère est encodé sur 5 octets, stocké en début de mémoire

FONTSET = [
    0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
    0x20, 0x60, 0x20, 0x20, 0x70,  # 1
    0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
    0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
    0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
    0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
    0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
    0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
    0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
    0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
    0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
    0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
    0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
    0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
    0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
    0xF0, 0x80, 0xF0, 0x80, 0x80,  # F
]

# Adresse de départ des programmes CHIP-8 en mémoire
PROGRAM_START = 0x200


class CPU:
    """
    Émule le processeur CHIP-8.

    Le CHIP-8 est une machine virtuelle des années 1970 conçue pour
    faciliter la programmation de jeux sur micro-ordinateurs de l'époque.
    """

    def __init__(self, display, keyboard):
        """
        Initialise tous les composants du CHIP-8.

        Args:
            display  : instance de Display, gère l'écran
            keyboard : instance de Keyboard, gère les touches
        """
        self.display = display
        self.keyboard = keyboard

        # --- Mémoire : 4096 octets (0x000 à 0xFFF) ---
        # 0x000-0x1FF : réservé (polices, système)
        # 0x200-0xFFF : programmes et données
        self.memory = [0] * 4096

        # --- 16 registres généraux 8 bits : V0 à VF ---
        # VF est souvent utilisé comme flag (carry, collision...)
        self.V = [0] * 16

        # --- Registre d'adresse 16 bits (pointeur mémoire) ---
        self.I = 0

        # --- Compteur de programme : pointe sur l'instruction courante ---
        self.PC = PROGRAM_START

        # --- Pile : stocke les adresses de retour des sous-routines ---
        self.stack = []

        # --- Timers 8 bits décrémentés à 60 Hz ---
        self.delay_timer = 0   # DT : timer de délai général
        self.sound_timer = 0   # ST : joue un son quand > 0

        # --- Flag : attente d'une touche (instruction FX0A) ---
        self.waiting_for_key = False
        self.waiting_register = 0  # registre où stocker la touche pressée

        # Chargement des polices en mémoire (adresses 0x000 à 0x04F)
        for i, byte in enumerate(FONTSET):
            self.memory[i] = byte


    # Chargement de ROM


    def load_rom(self, filepath):
        """
        Charge un fichier ROM CHIP-8 en mémoire à partir de 0x200.

        Args:
            filepath (str): chemin vers le fichier .ch8 ou .rom
        """
        with open(filepath, "rb") as f:
            data = f.read()

        for i, byte in enumerate(data):
            self.memory[PROGRAM_START + i] = byte

        print(f"[CPU] ROM chargée : {filepath} ({len(data)} octets)")


    # Cycle d'exécution principal


    def cycle(self):
        """
        Exécute un cycle : fetch → decode → execute.

        Si le CPU attend une touche (FX0A), on ne fait rien jusqu'à
        ce qu'une touche soit pressée.
        """
        # Mode attente de touche
        if self.waiting_for_key:
            key = self.keyboard.get_pressed_key()
            if key is not None:
                self.V[self.waiting_register] = key
                self.waiting_for_key = False
            return  # on attend, pas d'exécution

        # FETCH : lire l'opcode sur 2 octets (big-endian)
        high = self.memory[self.PC]
        low  = self.memory[self.PC + 1]
        opcode = (high << 8) | low

        # Avancer le compteur de programme (2 octets par instruction)
        self.PC += 2

        # DECODE & EXECUTE
        self._execute(opcode)


    # Décodage et exécution des opcodes


    def _execute(self, opcode):
        """
        Décode et exécute un opcode CHIP-8.

        Les opcodes sont identifiés par leur nibble de poids fort (4 bits).
        On extrait également les champs courants :
          - nnn : adresse 12 bits
          - n   : nibble bas (4 bits)
          - x   : index de registre (4 bits)
          - y   : index de registre (4 bits)
          - kk  : constante 8 bits

        Args:
            opcode (int): instruction 16 bits à exécuter
        """
        # Extraction des champs de l'opcode
        nnn = opcode & 0x0FFF          # adresse 12 bits
        n   = opcode & 0x000F          # nibble bas
        x   = (opcode & 0x0F00) >> 8   # index registre Vx
        y   = (opcode & 0x00F0) >> 4   # index registre Vy
        kk  = opcode & 0x00FF          # constante 8 bits

        # Sélection par nibble de poids fort
        kind = (opcode & 0xF000) >> 12

        if opcode == 0x00E0:
            # CLS : efface l'écran
            self.display.clear()

        elif opcode == 0x00EE:
            # RET : retour de sous-routine
            self.PC = self.stack.pop()

        elif kind == 0x1:
            # JP addr : saut inconditionnel à nnn
            self.PC = nnn

        elif kind == 0x2:
            # CALL addr : appel de sous-routine à nnn
            self.stack.append(self.PC)
            self.PC = nnn

        elif kind == 0x3:
            # SE Vx, kk : saute si Vx == kk
            if self.V[x] == kk:
                self.PC += 2

        elif kind == 0x4:
            # SNE Vx, kk : saute si Vx != kk
            if self.V[x] != kk:
                self.PC += 2

        elif kind == 0x5:
            # SE Vx, Vy : saute si Vx == Vy
            if self.V[x] == self.V[y]:
                self.PC += 2

        elif kind == 0x6:
            # LD Vx, kk : charge kk dans Vx
            self.V[x] = kk

        elif kind == 0x7:
            # ADD Vx, kk : Vx = Vx + kk (pas de carry)
            self.V[x] = (self.V[x] + kk) & 0xFF

        elif kind == 0x8:
            self._execute_8(x, y, n)

        elif kind == 0x9:
            # SNE Vx, Vy : saute si Vx != Vy
            if self.V[x] != self.V[y]:
                self.PC += 2

        elif kind == 0xA:
            # LD I, addr : charge nnn dans I
            self.I = nnn

        elif kind == 0xB:
            # JP V0, addr : saut à nnn + V0
            self.PC = nnn + self.V[0]

        elif kind == 0xC:
            # RND Vx, kk : Vx = random(0-255) AND kk
            self.V[x] = random.randint(0, 255) & kk

        elif kind == 0xD:
            # DRW Vx, Vy, n : dessine un sprite de n lignes à (Vx, Vy)
            self._draw_sprite(x, y, n)

        elif kind == 0xE:
            self._execute_E(x, kk)

        elif kind == 0xF:
            self._execute_F(x, kk)

        else:
            print(f"[CPU] Opcode inconnu : {opcode:#06x} (PC={self.PC:#06x})")

    def _execute_8(self, x, y, n):
        """Opcodes de la famille 8XYN (opérations arithmétiques/logiques)."""

        if n == 0x0:
            # LD Vx, Vy : Vx = Vy
            self.V[x] = self.V[y]

        elif n == 0x1:
            # OR Vx, Vy : Vx = Vx OR Vy
            self.V[x] |= self.V[y]

        elif n == 0x2:
            # AND Vx, Vy : Vx = Vx AND Vy
            self.V[x] &= self.V[y]

        elif n == 0x3:
            # XOR Vx, Vy : Vx = Vx XOR Vy
            self.V[x] ^= self.V[y]

        elif n == 0x4:
            # ADD Vx, Vy : Vx = Vx + Vy, VF = carry
            result = self.V[x] + self.V[y]
            self.V[0xF] = 1 if result > 0xFF else 0
            self.V[x] = result & 0xFF

        elif n == 0x5:
            # SUB Vx, Vy : Vx = Vx - Vy, VF = NOT borrow
            self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
            self.V[x] = (self.V[x] - self.V[y]) & 0xFF

        elif n == 0x6:
            # SHR Vx : Vx >>= 1, VF = bit perdu
            self.V[0xF] = self.V[x] & 0x1
            self.V[x] >>= 1

        elif n == 0x7:
            # SUBN Vx, Vy : Vx = Vy - Vx, VF = NOT borrow
            self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
            self.V[x] = (self.V[y] - self.V[x]) & 0xFF

        elif n == 0xE:
            # SHL Vx : Vx <<= 1, VF = bit perdu
            self.V[0xF] = (self.V[x] & 0x80) >> 7
            self.V[x] = (self.V[x] << 1) & 0xFF

    def _execute_E(self, x, kk):
        """Opcodes de la famille EX : entrées clavier."""

        if kk == 0x9E:
            # SKP Vx : saute si la touche V[x] est pressée
            if self.keyboard.is_key_pressed(self.V[x]):
                self.PC += 2

        elif kk == 0xA1:
            # SKNP Vx : saute si la touche V[x] n'est PAS pressée
            if not self.keyboard.is_key_pressed(self.V[x]):
                self.PC += 2

    def _execute_F(self, x, kk):
        """Opcodes de la famille FX : divers (timers, mémoire, I/O)."""

        if kk == 0x07:
            # LD Vx, DT : Vx = delay_timer
            self.V[x] = self.delay_timer

        elif kk == 0x0A:
            # LD Vx, K : attend une touche, stocke dans Vx
            self.waiting_for_key = True
            self.waiting_register = x

        elif kk == 0x15:
            # LD DT, Vx : delay_timer = Vx
            self.delay_timer = self.V[x]

        elif kk == 0x18:
            # LD ST, Vx : sound_timer = Vx
            self.sound_timer = self.V[x]

        elif kk == 0x1E:
            # ADD I, Vx : I = I + Vx
            self.I = (self.I + self.V[x]) & 0xFFFF

        elif kk == 0x29:
            # LD F, Vx : I pointe sur le sprite du chiffre Vx
            # Chaque caractère fait 5 octets, stockés depuis l'adresse 0
            self.I = self.V[x] * 5

        elif kk == 0x33:
            # LD B, Vx : stocke la représentation BCD de Vx en I, I+1, I+2
            # Ex : Vx=123 → memory[I]=1, memory[I+1]=2, memory[I+2]=3
            value = self.V[x]
            self.memory[self.I]     = value // 100
            self.memory[self.I + 1] = (value // 10) % 10
            self.memory[self.I + 2] = value % 10

        elif kk == 0x55:
            # LD [I], Vx : sauvegarde V0..Vx en mémoire à partir de I
            for i in range(x + 1):
                self.memory[self.I + i] = self.V[i]

        elif kk == 0x65:
            # LD Vx, [I] : charge V0..Vx depuis la mémoire à partir de I
            for i in range(x + 1):
                self.V[i] = self.memory[self.I + i]


    # Dessin de sprites


    def _draw_sprite(self, x, y, n):
        """
        Dessine un sprite à l'écran (opcode DXYN).

        Un sprite est une suite de n octets lus depuis memory[I].
        Chaque bit d'un octet correspond à un pixel.
        Le dessin se fait en XOR : si un pixel passe de allumé à éteint,
        VF est mis à 1 (détection de collision).

        Args:
            x (int): index du registre Vx (coordonnée X)
            y (int): index du registre Vy (coordonnée Y)
            n (int): nombre de lignes du sprite (hauteur)
        """
        pos_x = self.V[x]
        pos_y = self.V[y]
        self.V[0xF] = 0  # reset du flag de collision

        for row in range(n):
            sprite_byte = self.memory[self.I + row]

            for col in range(8):
                # Vérifie si le bit courant du sprite est allumé (1)
                if sprite_byte & (0x80 >> col):
                    collision = self.display.toggle_pixel(pos_x + col, pos_y + row)
                    if collision:
                        self.V[0xF] = 1  # collision détectée

    # Mise à jour des timers (à appeler à 60 Hz)


    def update_timers(self):
        """
        Décrémente les timers DT et ST de 1 à chaque appel.
        Doit être appelé 60 fois par seconde.
        """
        if self.delay_timer > 0:
            self.delay_timer -= 1

        if self.sound_timer > 0:
            self.sound_timer -= 1
