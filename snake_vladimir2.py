# Importation des bibliothèques, ne pas modifier
import pygame
import math
import random
import tkinter as tk
from tkinter import ttk
import time

max_tick = [10, 12, 14, 16, 18]
cote_dif = [11, 13, 16, 19, 25]

# Variables globales qui seront recalculées au lancement
cote = 0
unite = 0
largeur_zone = 0
hauteur_zone = 0
largeur_fenetre = 0
hauteur_fenetre = 0
largeur_mur_de_gauche = 0
largeur_mur_de_droite = 0

# Variables globales pour les couleurs modifiables par les skins
couleur_nourriture = (83, 62, 45)
couleur_serpent = (162, 112, 53)
couleur_fond = (221, 202, 125)
couleur_murs = (184, 139, 74)


def apply_skin(skin="arcade"):
    global couleur_nourriture, couleur_serpent, couleur_fond, couleur_murs
    match skin:
        case "savanna":
            couleur_nourriture = (83, 62, 45)
            couleur_serpent = (162, 112, 53)
            couleur_fond = (221, 202, 125)
            couleur_murs = (184, 139, 74)
        case "arcade":
            couleur_nourriture = (174, 32, 18)
            couleur_serpent = (0, 119, 182)
            couleur_fond = (167, 201, 87)
            couleur_murs = (106, 153, 78)
        case "iced_valley":
            couleur_nourriture = (184, 219, 217)
            couleur_serpent = (47, 69, 80)
            couleur_fond = (244, 244, 249)
            couleur_murs = (144, 224, 239)
        case "crimson_volcano":
            couleur_nourriture = (56, 4, 14)
            couleur_serpent = (128, 14, 19)
            couleur_fond = (247, 181, 56)
            couleur_murs = (216, 87, 42)
        case "dark_is_the_night":
            couleur_nourriture = (157, 78, 221)
            couleur_serpent = (36, 0, 70)
            couleur_fond = (119, 141, 169)
            couleur_murs = (27, 38, 59)
        case "dead":
            couleur_nourriture = (214,40,40)
            couleur_serpent = (214,40,40)
            couleur_fond = (0,0,0)
            couleur_murs = (0,0,0)

def invert_direction(dire):
    match dire:
        case "right": return "left"
        case "left":  return "right"
        case "down":  return "up"
        case "up":    return "down"


def dessine_carre(x: int, y: int, couleur: tuple, fenetre):
    pygame.draw.rect(
        surface=fenetre,
        color=couleur,
        rect=(x * unite, y * unite, unite+1, unite+1)
    )


def dessiner_rectangle(x, y, x2, y2, couleur, fenetre):
    pygame.draw.rect(
        surface=fenetre,
        color=couleur,
        rect=(x * unite, y * unite, (x2 - x) * unite, (y2 - y) * unite)
    )


def dessiner_cercle(x, y, couleur, rayon, fenetre):
    pygame.draw.circle(fenetre, couleur, (x * unite + unite / 2, y * unite + unite / 2), int(rayon * unite))


def dessiner_plusieurs_carres(positions: list, couleur: tuple, fenetre):
    for x, y in positions:
        dessine_carre(x, y, couleur, fenetre)


def entier_aleatoire(min_val: int, max_val: int) -> int:
    return random.randint(min_val, max_val)


def generate_random_co():
    return (entier_aleatoire(largeur_mur_de_gauche, largeur_mur_de_gauche + largeur_zone - 1), entier_aleatoire(0, hauteur_zone - 1))


def afficher_message(fenetre, message: str, couleur: tuple, taille: int = 40,co = [25,0]):
    # Remplacement de 3*unite par une taille fixe en pixels pour éviter les bugs de police trop grande
    myfont = pygame.font.Font("font.otf", taille)
    fenetre.blit(myfont.render(message, True, couleur), co)


def draw_bwalls(fenetre):
    dessiner_rectangle(0, 0, largeur_mur_de_gauche, hauteur_fenetre, couleur_murs, fenetre)
    dessiner_rectangle(largeur_mur_de_gauche + largeur_zone, 0, largeur_fenetre, hauteur_fenetre, couleur_murs, fenetre)


def calculer_dir(event, dire):
    match event.key:
        case pygame.K_z | pygame.K_UP:
            if dire != "down": return "up"
        case pygame.K_s | pygame.K_DOWN:
            if dire != "up": return "down"
        case pygame.K_d | pygame.K_RIGHT:
            if dire != "left": return "right"
        case pygame.K_q | pygame.K_LEFT:
            if dire != "right": return "left"
    return False


def calculer_pos(pos: tuple, direction: str):
    match direction:
        case "up":    return (pos[0], pos[1] - 1)
        case "down":  return (pos[0], pos[1] + 1)
        case "right": return (pos[0] + 1, pos[1])
        case "left":  return (pos[0] - 1, pos[1])


def is_fed(pos: list, position_pomme: tuple):
    return position_pomme in pos


def is_touching(positions: list, pos):
    return pos in positions


def is_touching_anything(pos, positions):
    for i in positions:
        if isinstance(i, tuple) and i == pos:
            return True
        elif isinstance(i, list) and is_touching(i, pos):
            return True
    return False


def is_on_board(pos: tuple):
    return largeur_mur_de_gauche <= pos[0] < largeur_mur_de_gauche + largeur_zone and 0 <= pos[1] < hauteur_zone


def invert_pos(pos):
    x, y = pos
    # Remplacement de x_zone_offset par largeur_mur_de_gauche
    if x < largeur_mur_de_gauche:
        x = largeur_mur_de_gauche + largeur_zone - 1
    elif x >= largeur_mur_de_gauche + largeur_zone:
        x = largeur_mur_de_gauche
    if y < 0:
        y = hauteur_zone - 1
    elif y >= hauteur_zone:
        y = 0
    return (x, y)


def tour_de_jeu(positions_serpent: list, jeu_fini: bool, direction_serpent: str, 
                position_pomme: tuple, fenetre, score, wall_pos, tick, gamemode, difficulty) -> tuple:
    
    dessiner_cercle(position_pomme[0], position_pomme[1], couleur_nourriture, 0.65, fenetre)
    afficher_message(fenetre, str(score), (255, 255, 255), 240)
    
    pygame.display.update()
    dessiner_plusieurs_carres(wall_pos, couleur_murs, fenetre)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jeu_fini = True
        if event.type == pygame.KEYDOWN:
            nouvelle_dir = calculer_dir(event, direction_serpent)
            if nouvelle_dir:
                direction_serpent = nouvelle_dir

    prochaine_pos = calculer_pos(positions_serpent[-1], direction_serpent)

    if is_on_board(prochaine_pos):
        positions_serpent.append(prochaine_pos)
    elif gamemode == "dimensionnal_error":
        if difficulty < 3:
            positions_serpent.append(invert_pos(prochaine_pos))
        else:
            positions_serpent.append(generate_random_co())
    else:
        jeu_fini = True
        return positions_serpent, jeu_fini, direction_serpent, position_pomme, wall_pos, tick

    positions_corps = positions_serpent[:-1]
    if is_touching(positions_corps, positions_serpent[-1]):
        jeu_fini = True
        
    if not is_fed(positions_serpent, position_pomme): 
        del positions_serpent[0]
    else:
        position_pomme = generate_random_co()
        if tick < max_tick[difficulty]:
            tick += (difficulty + 1) / 2
        while is_touching(positions_serpent, position_pomme) or is_touching(wall_pos, position_pomme):
            position_pomme = generate_random_co()
            
        if gamemode == "bricky_situation":
            for i in range(difficulty + 1):
                new_wall = generate_random_co()
                while is_touching_anything(new_wall, [positions_serpent, position_pomme, wall_pos]):
                    new_wall = generate_random_co()
                wall_pos.append(new_wall)
            
        if gamemode == "wrong_way":
            positions_serpent.reverse()
            direction_serpent = invert_direction(direction_serpent)
        
    if is_touching(wall_pos, positions_serpent[-1]):
        jeu_fini = True
    
    return positions_serpent, jeu_fini, direction_serpent, position_pomme, wall_pos, tick


def start(gamemode="classic", skin="arcade", dif=1):
    # On déclare toutes les variables à modifier au niveau global
    global cote, unite, largeur_zone, hauteur_zone, largeur_fenetre, hauteur_fenetre, largeur_mur_de_gauche, largeur_mur_de_droite
    
    apply_skin(skin)
    
    # Étape d'initialisation dynamique basée sur la difficulté choisie
    cote = cote_dif[dif]
    unite = 1080 / cote
    largeur_zone = cote
    hauteur_zone = cote
    largeur_fenetre = 1920 / unite
    hauteur_fenetre = 1080 / unite
    largeur_mur_de_gauche = math.ceil((largeur_fenetre - hauteur_fenetre) / 2)
    largeur_mur_de_droite = math.ceil(largeur_fenetre - (hauteur_fenetre + largeur_mur_de_gauche)) - 1

    positions_serpent = [(largeur_mur_de_gauche, 1), (largeur_mur_de_gauche, 1), (largeur_mur_de_gauche, 1), (largeur_mur_de_gauche, 1)]
    wall_pos = []
    direction_serpent = "right"
    position_pomme = generate_random_co()

    pygame.init()
    clock = pygame.time.Clock()  
    tick = 7
    fenetre = pygame.display.set_mode((int(largeur_fenetre * unite), int(hauteur_fenetre * unite)), pygame.FULLSCREEN)
    pygame.display.set_caption("Snake")
    
    jeu_fini = False
    while not jeu_fini:  
        fenetre.fill(couleur_fond)
        score = len(positions_serpent) - 4
        
        draw_bwalls(fenetre)
        
        dessiner_plusieurs_carres(wall_pos, couleur_murs, fenetre)
        dessiner_plusieurs_carres(positions_serpent, couleur_serpent, fenetre)
        
        positions_serpent, jeu_fini, direction_serpent, position_pomme, wall_pos, tick = tour_de_jeu(
            positions_serpent, jeu_fini, direction_serpent, position_pomme, fenetre, score, wall_pos, tick, gamemode, dif,
        )
        clock.tick(tick)
        
    apply_skin("dead")
    
    fenetre.fill(couleur_fond)
    draw_bwalls(fenetre)
    dessiner_cercle(position_pomme[0], position_pomme[1], couleur_nourriture, 0.65, fenetre)
    dessiner_plusieurs_carres(wall_pos, couleur_murs, fenetre)
    dessiner_plusieurs_carres(positions_serpent, couleur_serpent, fenetre)
    afficher_message(fenetre,"you",(214,40,40),240)
    afficher_message(fenetre,"got",(214,40,40),240,[25,240])
    afficher_message(fenetre,"slaid",(214,40,40),240,[25,480])
    pygame.display.update()
    

    time.sleep(1)
    pygame.quit()


# --- Interface Graphique Tkinter ---
liste_gamemodes = ['classic', 'bricky_situation', 'wrong_way', 'dimensionnal_error']
liste_skins = ['arcade', 'savanna', 'iced_valley', 'crimson_volcano', 'dark_is_the_night']
liste_difficulty = ['peaceful', 'riskful', 'bloodstained', 'mercyless', 'THE_PURGE']

fentk = tk.Tk()
fentk.title("SNAKE : PARAMETRAGE DE LA PARTIE")
fentk.geometry("400x350")

gamemode_label = tk.Label(fentk, text="GAMEMODE :", font=("Arial", 12, "bold"))
gamemode_label.pack(pady=5)

gamemode_menu = ttk.Combobox(fentk, values=liste_gamemodes, state="readonly")
gamemode_menu.current(0)
gamemode_menu.pack(pady=10)

skin_label = tk.Label(fentk, text="SKIN :", font=("Arial", 12, "bold"))
skin_label.pack(pady=5)

skin_menu = ttk.Combobox(fentk, values=liste_skins, state="readonly")
skin_menu.current(0)
skin_menu.pack(pady=10)

dif_label = tk.Label(fentk, text="DIFFICULTY :", font=("Arial", 12, "bold"))
dif_label.pack(pady=5)

dif_menu = ttk.Combobox(fentk, values=liste_difficulty, state="readonly")
dif_menu.current(0)
dif_menu.pack(pady=10)


def _on_button_pressed():
    mode_choisi = gamemode_menu.get()
    skin_choisi = skin_menu.get()
    difficulte_choisi = dif_menu.get()
    
    fentk.destroy() 
    start(gamemode=mode_choisi, skin=skin_choisi, dif=liste_difficulty.index(difficulte_choisi))


start_button = tk.Button(fentk, text="START GAME", font=("Arial", 10, "bold"), command=_on_button_pressed)
start_button.pack(side="bottom", pady=30)

fentk.mainloop()