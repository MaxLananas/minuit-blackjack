from jeu.manche import Etat


def tutorial_step(partie):
    if partie.etat == Etat.MISE and not partie.mise_en_attente:
        return (
            "1 / 5  •  LA MISE",
            "But du jeu : battre la banque en approchant 21\nsans le dépasser. Clique un jeton doré pour miser ;\ncombine-les si tu veux augmenter ta mise.",
            "jetons",
        )
    if partie.etat == Etat.MISE:
        return (
            "2 / 5  •  À TABLE !",
            "Ta mise est prête. Elle reste engagée pour la manche.\nClique sur DISTRIBUER et regarde les cartes arriver.",
            "distribuer",
        )
    if partie.etat == Etat.DISTRIBUTION:
        return (
            "3 / 5  •  LES CARTES ARRIVENT",
            "Deux cartes pour toi et les rivaux. La banque\nen montre une et en garde une face cachée.\nTon score est affiché à droite.",
            None,
        )
    if partie.etat == Etat.TOUR_JOUEUR:
        return (
            "4 / 5  •  À TOI DE JOUER",
            "Vise 21 sans le dépasser. TIRER : une carte de plus.\nRESTER : tu gardes ta main. DOUBLER : tu doubles\nta mise pour une carte. Avec une paire, SÉPARER\npermet de jouer deux mains.",
            "actions",
        )
    if partie.etat in {Etat.TOUR_RIVAUX, Etat.TOUR_CROUPIER, Etat.REGLEMENT}:
        return (
            "5 / 5  •  LE VERDICT APPROCHE",
            "Les rivaux tentent aussi de battre la banque.\nLe croupier tire jusqu'à 17, puis s'arrête.\nAu-dessus de 21, ta main saute. Regarde le bilan\npour savoir qui rafle les jetons.",
            None,
        )
    return (
        "LA MANCHE EST FINIE",
        "C'est l'heure du bilan : tu verras combien tu as gagné.\nRejoue la même mise ou prépare-en une nouvelle.\nTu peux fermer l'aide quand tu veux.",
        "resultat",
    )
