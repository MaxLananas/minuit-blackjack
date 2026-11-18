# Minuit

Minuit est un jeu de blackjack en 3D réalisé en Python avec Ursina. C'est un projet de NSI : les règles de la partie, l'interface et les objets du jeu sont séparés dans des modules différents.

Les jetons sont virtuels : aucune mise d'argent réelle n'est utilisée.

## Lancer le jeu

Sur Windows 64 bits, double-clique sur `Jouer.bat`. Python et les bibliothèques nécessaires sont fournis dans le dossier `python`, donc rien n'est à installer. Garde tous les dossiers du projet ensemble.

Le guide de lancement et les commandes de base sont dans [lis-moi.md](lis-moi.md).

## Organisation du code

- `jeu/` contient les règles du blackjack, les cartes et le déroulement des manches.
- `objets/` contient les éléments 3D de la table et des joueurs.
- `ecran/` contient les menus, l'interface, les paramètres et le tutoriel.
- `ressources/` contient les modèles, les images, les sons et les polices.
- `python/` contient le moteur Python et les bibliothèques embarquées nécessaires au lancement.

Le solde de départ se règle dans les paramètres. Un montant personnalisé peut aller jusqu'à 1 000 000 jetons.
