from functools import lru_cache
from random import Random

from jeu.cartes import Carte

DIFFICULTES = ("facile", "normal", "expert")


def _total(base, a_un_as):
    if a_un_as and base + 10 <= 21:
        return base + 10
    return base


def _compter_inconnues(visible):
    counts = [4] * 9 + [16]
    for carte in visible:
        if not isinstance(carte, Carte):
            raise TypeError("La stratégie ne doit recevoir que des cartes visibles.")
        counts[carte.valeur_base - 1] -= 1
    if any(count < 0 for count in counts):
        raise ValueError("Cartes visibles incompatibles avec un paquet de 52 cartes.")
    return tuple(counts)


def _action_paire(main, visible_croupier, autorisees):
    if "separer" not in autorisees:
        return None
    rang = main.cartes[0].rang
    if rang in {"A", "8"}:
        return "separer"
    if rang == "9" and visible_croupier in {2, 3, 4, 5, 6, 8, 9}:
        return "separer"
    if rang in {"2", "3", "7"} and 2 <= visible_croupier <= 7:
        return "separer"
    if rang == "6" and 2 <= visible_croupier <= 6:
        return "separer"
    if rang == "4" and visible_croupier in {5, 6}:
        return "separer"
    return None


def action_normale(main, carte_croupier, autorisees):
    visible_croupier = 11 if carte_croupier.rang == "A" else carte_croupier.valeur_base
    pair = _action_paire(main, visible_croupier, autorisees)
    if pair:
        return pair
    valeur, souple = main.score
    if "doubler" in autorisees:
        if not souple and (
            (valeur == 9 and 3 <= visible_croupier <= 6)
            or (valeur == 10 and 2 <= visible_croupier <= 9)
            or (valeur == 11 and visible_croupier <= 10)
        ):
            return "doubler"
        if (
            souple
            and 13 <= valeur <= 18
            and (
                (valeur <= 16 and visible_croupier in (5, 6))
                or (valeur in (17, 18) and 3 <= visible_croupier <= 6)
            )
        ):
            return "doubler"
    if souple:
        if valeur <= 17 or (valeur == 18 and visible_croupier in (9, 10, 11)):
            return "tirer"
        return "rester"
    if valeur <= 11:
        return "tirer"
    if valeur == 12:
        return "rester" if 4 <= visible_croupier <= 6 else "tirer"
    if 13 <= valeur <= 16:
        return "rester" if 2 <= visible_croupier <= 6 else "tirer"
    return "rester"


def probabilites_croupier(carte_croupier, visible):
    counts = _compter_inconnues(visible)
    remaining = sum(counts)
    if remaining <= 0:
        raise ValueError("Aucune carte inconnue pour calculer la distribution.")
    weights = tuple(count / remaining for count in counts)

    @lru_cache(maxsize=256)
    def finish(base, a_un_as):
        valeur = _total(base, a_un_as)
        if valeur >= 17:
            outcome = [0.0] * 6
            outcome[5 if valeur > 21 else valeur - 17] = 1.0
            return tuple(outcome)
        totals = [0.0] * 6
        for index, probability in enumerate(weights):
            if not probability:
                continue
            child = finish(base + index + 1, a_un_as or index == 0)
            for i, part in enumerate(child):
                totals[i] += probability * part
        return tuple(totals)

    visible_croupier = carte_croupier.valeur_base
    allowed_holes = list(counts)
    if carte_croupier.rang == "A":
        allowed_holes[9] = 0
    elif visible_croupier == 10:
        allowed_holes[0] = 0
    total_holes = sum(allowed_holes)
    if not total_holes:
        return (0, 0, 0, 0, 0, 1)
    outcomes = [0.0] * 6
    for index, count in enumerate(allowed_holes):
        if not count:
            continue
        child = finish(
            visible_croupier + index + 1, visible_croupier == 1 or index == 0
        )
        for i, part in enumerate(child):
            outcomes[i] += count / total_holes * part
    return tuple(outcomes)


def action_experte(main, carte_croupier, visible, autorisees):
    visible_croupier = 11 if carte_croupier.rang == "A" else carte_croupier.valeur_base
    pair = _action_paire(main, visible_croupier, autorisees)
    if pair:
        return pair
    counts = _compter_inconnues(visible)
    if not sum(counts):
        return "rester"
    outcomes = probabilites_croupier(carte_croupier, visible)

    def gain_rester(base, ace):
        total = _total(base, ace)
        if total > 21:
            return -1.0
        gain = 0.0
        for croupier, probability in zip(range(17, 22), outcomes[:5]):
            if total > croupier:
                gain += probability
            elif total < croupier:
                gain -= probability
        return outcomes[5] + gain

    @lru_cache(maxsize=5000)
    def gain_tirer(base, ace, cartes_restantes, depth):
        remaining = sum(cartes_restantes)
        if not remaining:
            return gain_rester(base, ace)
        resultat = 0.0
        for index, count in enumerate(cartes_restantes):
            if not count:
                continue
            valeur = index + 1
            next_base = base + valeur
            next_ace = ace or valeur == 1
            updated = list(cartes_restantes)
            updated[index] -= 1
            best = gain_rester(next_base, next_ace)
            if _total(next_base, next_ace) < 21 and depth > 1:
                best = max(
                    best, gain_tirer(next_base, next_ace, tuple(updated), depth - 1)
                )
            resultat += count / remaining * best
        return resultat

    base = sum(carte.valeur_base for carte in main.cartes)
    a_un_as = any(carte.rang == "A" for carte in main.cartes)
    choices = {"rester": gain_rester(base, a_un_as)}
    if "tirer" in autorisees:
        choices["tirer"] = gain_tirer(base, a_un_as, counts, 3)
    if "doubler" in autorisees:
        total = sum(counts)
        choices["doubler"] = 2 * sum(
            count / total * gain_rester(base + index + 1, a_un_as or index == 0)
            for index, count in enumerate(counts)
            if count
        )
    return max(choices, key=choices.get)


def choisir_action(main, carte_croupier, visible, autorisees, difficulte, hasard=None):
    if difficulte not in DIFFICULTES:
        raise ValueError("Difficulté inconnue.")
    if not {"tirer", "rester"}.issubset(autorisees):
        raise ValueError("La main doit pouvoir tirer ou rester.")
    if difficulte == "expert":
        return action_experte(main, carte_croupier, visible, autorisees)
    if difficulte == "normal":
        return action_normale(main, carte_croupier, autorisees)
    generator = hasard or Random()
    if "separer" in autorisees and main.cartes[0].rang == "A":
        return "separer"
    if "doubler" in autorisees and main.valeur == 11 and generator.random() < 0.45:
        return "doubler"
    threshold = 15 if generator.random() < 0.7 else 16
    return "tirer" if main.valeur < threshold else "rester"
