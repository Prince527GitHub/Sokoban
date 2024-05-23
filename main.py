from copy import deepcopy
import termios
import base64
import json
import time
import tty
import sys
import os

# Couleur blanc
def fgWhite(string):
    return f"\x1b[37m{string}\x1b[0m"

# Couleur vert
def fgGreen(string):
    return f"\x1b[32m{string}\x1b[0m"

# Couleur rouge
def fgRed(string):
    return f"\x1b[31m{string}\x1b[0m"

# Colour custom RGB
def fgRGB(string, r = 0, g = 0, b = 0):
    return f"\x1b[38;2;{r};{g};{b}m{string}\x1b[0m"

# Fonction pour effacer l'écran
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

# Fonction permettant de recueillir les données de l'utilisateur 
def getInput(message):
    # Si l'utilisateur est sur windows juste utiliser un normal input
    if os.name == "nt":
        char = input(message)
    else:
        # Si l'utilisateur est sur linux/mac nous écouterons un événement pour recevoir le texte sans appuyer "Enter"
        print(message)

        terminal = sys.stdin.fileno()
        settings = termios.tcgetattr(terminal)

        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(terminal, termios.TCSADRAIN, settings)

    return char

# Fonction pour afficher l'état du jeu
def show(array, text = ""):
    # Effacer l'écran
    clear()

    # Afficher le texte extra si il y en a
    if text:
        print(text)

    # Les couleurs RGB des caractères
    colors = {
        "▒": [11, 184, 72],
        "x": [248, 33, 71],
    }

    # Ces deux boucles for me donne accès a chaque caractère de l'array
    for x in range(len(array)):
        for y in range(len(array[x])):
            color = colors.get(array[x][y])

            # Si le caractère a une couleur on va l'utiliser avec la founction RGB si non on affiche le caractère normal
            if color:
                print(fgRGB(array[x][y], color[0], color[1], color[2]), end="")
            else:
                print(array[x][y], end="")

            # Lorsque j'ai atteint le dernier caractère du ligne je bouge a une nouvelle ligne
            if y + 1 == len(array[x]):
                print("\n", end="")

# Fonction pour vérifier si le joueur a gagné
def checkForWin(level, default):
    total = 0
    completed = 0

    # Cette boucle for vérifie l'état par défaut du niveau et obtient le nombre de "x" (point final)
    for x in range(len(default)):
        for y in range(len(default[x])):
            if default[x][y] == "x":
                total += 1

    # Pendant que cette boucle for vérifie l'état du niveau pour obtenir le nombre de point final completés
    for x in range(len(default)):
        for y in range(len(default[x])):
            if default[x][y] == "x" and level[x][y] == "▒":
                completed += 1

    return completed == total

# Fonction pour ajouter un niveau
def add(levels, lang):
    # Effacer l'écran
    clear()

    print(f"Level editor: {fgRGB('https://prince527github.github.io/Sokoban/index.html?lang=en', 0, 0, 255)}\n" if lang == "en" else f"Éditeur de niveaux: {fgRGB('https://prince527github.github.io/Sokoban/index.html?lang=fr', 0, 0, 255)}\n")

    level = input("Paste level code? " if lang == "en" else "Coller le code de niveau? ")

    # Retourner au menu si l'utilisateur tape "q"
    if level == "q":
        print("Returning to level select menu..." if lang == "en" else "Retour au menu de sélection de niveau...")

        # Attendre 1,5 seconde
        time.sleep(1.5)

        return menu(levels, lang)

    try:
        # Décoder la chaîne base64 puis l'analyser en json
        object = json.loads(base64.b64decode(level))
    except:
        print(fgRed("Invalid level code." if lang == "en" else "Code de niveau non valide."))

        # Attendre 1,5 seconde
        time.sleep(1.5)

        return add(levels)

    # si le niveau est décodé ajouter le au array
    levels.append(object)

    print(fgGreen("Added level!" if lang == "en" else "Niveau supplémentaire!"))

    # Attendre 1,5 seconde
    time.sleep(1.5)

    # Retourner au menu
    return menu(levels, lang)

# Fonction qui gère le jeu
def game(level, default, lang, moves = 0):
    moved = False

    # Afficher l'état du niveau avec le nombre de mouvements
    show(level, f"Moves: {moves}" if lang == "en" else f"Mouvements: {moves}")

    # Obtenir le input de l'utilisateur
    direction = getInput("Where do you want to go? " if lang == "en" else "Où voulez-vous aller? ")

    # N'obtenir que la première lettre juste nécessaire pour windows
    try:
        direction = direction[0]
    except:
        direction = None

    if direction == "r":
        # Remettre le niveau au défaut
        level = deepcopy(default)

    elif direction == "q":
        # Afficher l'état du niveau avec le nombre de mouvements
        show(level, f"Moves: {moves}" if lang == "en" else f"Mouvements: {moves}")

        print("Returning to level select menu..." if lang == "en" else "Retour au menu de sélection de niveau...")

        # Attendre 1,5 seconde
        time.sleep(1.5)

        # Retourner au menu avec False car l'utilisateur n'a pas gagné
        return False

    # Boucles for pour parcourir le niveau
    for x in range(len(level)):
        for y in range(len(level[x])):
            # Vérifier si le joueur a déjà bougé
            if moved == True:
                break

            # Bouger en haut
            if direction == "w":
                # Trouver l'utilisateur et vérifier si l'espace est vide
                if level[x][y] == "P" and level[x - 1][y] == " ":
                    # Déplacer le joueur sur le array
                    level[x - 1][y] = "P"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est vide
                elif level[x][y] == "P" and level[x - 1][y] == "▒" and level[x - 2][y] == " ":
                    # Déplacer le joueur/la boîte sur le tableau
                    level[x - 1][y] = "P"
                    level[x - 2][y] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est un point final
                elif level[x][y] == "P" and level[x - 1][y] == "▒" and level[x - 2][y] == "x":
                    # Déplacer le joueur/la boîte sur le tableau
                    level[x - 1][y] = "P"
                    level[x - 2][y] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1

            # Bouger a gauche
            elif direction == "a":
                # Trouver l'utilisateur et vérifier si l'espace est vide
                if level[x][y] == "P" and level[x][y - 1] == " ":
                    # Déplacer le joueur sur le array
                    level[x][y - 1] = "P"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est vide
                elif level[x][y] == "P" and level[x][y - 1] == "▒" and level[x][y - 2] == " ":
                    # Déplacer le joueur/la boîte sur le array
                    level[x][y - 1] = "P"
                    level[x][y - 2] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est un point final
                elif level[x][y] == "P" and level[x][y - 1] == "▒" and level[x][y - 2] == "x":
                    # Déplacer le joueur/la boîte sur le array
                    level[x][y - 1] = "P"
                    level[x][y - 2] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1

            # Bouger en bas
            elif direction == "s":
                # Trouver l'utilisateur et vérifier si l'espace est vide
                if level[x][y] == "P" and level[x + 1][y] == " ":
                    # Déplacer le joueur sur le array
                    level[x + 1][y] = "P"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est vide
                elif level[x][y] == "P" and level[x + 1][y] == "▒" and level[x + 2][y] == " ":
                    # Déplacer le joueur/la boîte sur le array
                    level[x + 1][y] = "P"
                    level[x + 2][y] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est un point final
                elif level[x][y] == "P" and level[x + 1][y] == "▒" and level[x + 2][y] == "x":
                    # Déplacer le joueur/la boîte sur le array
                    level[x + 1][y] = "P"
                    level[x + 2][y] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1

            # Bouger a droit
            elif direction == "d":
                # Trouver l'utilisateur et vérifier si l'espace est vide
                if level[x][y] == "P" and level[x][y + 1] == " ":
                    # Déplacer le joueur sur le array
                    level[x][y + 1] = "P"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est vide
                elif level[x][y] == "P" and level[x][y + 1] == "▒" and level[x][y + 2] == " ":
                    # Déplacer le joueur/la boîte sur le array
                    level[x][y + 1] = "P"
                    level[x][y + 2] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1
                # Trouver l'utilisateur et la boîte à côté de l'utilisateur et vérifier si l'espace est un point final
                elif level[x][y] == "P" and level[x][y + 1] == "▒" and level[x][y + 2] == "x":
                    # Déplacer le joueur/la boîte sur le array
                    level[x][y + 1] = "P"
                    level[x][y + 2] = "▒"
                    level[x][y] = " "
                    moved = True
                    moves += 1

    # Vérifier si l'utilisateur a gagné
    win = checkForWin(level, default)

    if (win == True):
        # Afficher l'état du niveau avec le nombre de mouvements
        show(level, f"Moves: {moves}" if lang == "en" else f"Mouvements: {moves}")

        print(fgGreen("You win!" if lang == "en" else "Vous avez gagné!"))

        # Attendre 1,5 seconde
        time.sleep(1.5)

        # Retourner au menu avec True car l'utilisateur a gagné
        return win

    # Passer à l'image/input suivante
    return game(level, default, lang, moves)

# Fonction pour afficher le menu
def menu(levels, lang, completed = []):
    # Effacer l'écran
    clear()

    # Si l'utilisateur n'a pas complété aucun niveau, afficher les contrôles
    if len(completed) == 0:
        print(f"{fgRGB('Controls', 0, 0, 255)}\n> \"w\" \"a\" \"s\" \"d\" to move\n> \"q\" to exit/return to menu\n> \"1-{len(levels)}\" to select the level\n> \"a\" to add a custom level\n" if lang == "en" else f"{fgRGB('Contrôles', 0, 0, 255)}\n> « w » « a » « s » « d » pour se déplacer\n> « q » pour quitter/retourner au menu\n> « 1-4 » pour sélectionner le niveau\n> « a » pour ajouter un niveau personnalisé\n")

    buttons = [[], [], []]

    for i in range(len(levels)):
        # Si le array n'est pas de la même longueur ajouter Faux
        while len(completed) <= i:
            completed.append(False)

        # Calculer le nombre de murs nécessaires
        wall = len(str(i + 1)) * "█"

        # Si le niveau est complétés, utilisée vert, sinon rouge.
        if completed[i] == True:
            # Ajouter chaque ligne du bouton au array
            buttons[0].append(fgGreen(f"████{wall}"))
            buttons[1].append(fgGreen(f"█ {i + 1} █"))
            buttons[2].append(fgGreen(f"████{wall}"))
        else:
            # Ajouter chaque ligne du bouton au array
            buttons[0].append(fgRed(f"████{wall}"))
            buttons[1].append(fgRed(f"█ {i + 1} █"))
            buttons[2].append(fgRed(f"████{wall}"))

    # Afficher le menu des boutons
    for i in range(len(buttons)):
        print(" ".join(buttons[i]))

    selection = input("What level do you want to play? " if lang == "en" else "Quel niveau voulez-vous jouer? ")

    if selection == "q":
        exit()
    elif selection == "a":
        return add(levels, lang)

    # Convertir le input de l'utilisateur a un int, sinon montrer à nouveau le menu
    try:
        selection = int(selection)
    except ValueError:
        menu(levels, lang)

    # Vérifier si le niveau existe
    for i in range(len(levels)):
        level = levels[i]

        if selection == i + 1:
            # Démarrer le niveau
            state = game(deepcopy(level), deepcopy(level), lang)

            # Vérifier si l'utilisateur a gagné
            if state == True:
                completed[i] = True

    # Retourner au menu
    menu(levels, lang, completed)

# Les niveaux intégrés 
levels = [
    [
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", " ", " ", "P", " ", " ", "▒", " ", " ", " ", " ", " ", " ", " ", " ", "x", " ", " ", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"]
    ],
    [
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", " ", " ", "▒", " ", " ", " ", " ", " ", " ", " ", "x", "█", " ", "x", "█"],
        ["█", " ", " ", "▒", " ", " ", "P", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", "▒", " ", " ", " ", " ", " ", "x", "█", " ", " ", "█"],
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"]
    ],
    [
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", "▒", " ", " ", " ", " ", " ", "▒", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", " ", " ", "▒", " ", " ", " ", " ", "▒", " ", " ", " ", " ", " ", "▒", " ", "x", " ", "█"],
        ["█", "P", " ", "█", " ", "▒", " ", " ", " ", " ", " ", " ", "▒", " ", " ", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"]
    ],
    [
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "x", " ", " ", " ", " ", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", "█", "█", "█", "█", "█", "█", " ", " ", "█"],
        ["█", " ", " ", " ", "█", " ", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", " ", " ", " ", "█", " ", " ", "█", "█", "█", "█", "█", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█", "█", " ", " ", " ", " ", " ", " ", " ", "█", "█", " ", "█", " ", " ", "█", "█", "█", "█", "█", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", "█", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", " ", " ", " ", "▒", " ", " ", " ", " ", "█", " ", " ", " ", " ", "█", " ", " ", " ", " ", " ", " ", "P", " ", " ", "█"],
        ["█", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", " ", "█"],
        ["█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█", "█"]
    ]
]

def language():
    # Effacer l'écran
    clear()

    print(f"{fgRGB('Language/langue', 0, 0, 255)}\n> \"en\" => \"English\"\n> \"fr\" => \"Français\"\n")

    lang = input("Select a language/Sélectionner une langue: ")

    if lang == "q":
        return exit()
    # Vérifier si le texte est une langue valide
    elif lang != "en" and lang != "fr":
        # Effacer l'écran
        clear()

        print(fgRed("Incorrect language/Langue incorrecte"))

        # Attendre 1,5 seconde
        time.sleep(1.5)

        # Recommencer la selection de langue
        return language()

    # Effacer l'écran
    clear()

    # Montrer la langue sélectionnée
    print(fgGreen("Selected \"English\"" if lang == "en" else "Sélectionné \"Français\""))

    # Attendre 1,5 seconde
    time.sleep(1.5)

    # Afficher le menu
    return menu(levels, lang)

# Commancer le programme
language()