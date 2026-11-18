from enum import StrEnum
from random import Random


class Couleur(StrEnum):

    PIQUE = "pique"
    COEUR = "coeur"
    CARREAU = "carreau"
    TREFLE = "trefle"


RANGS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")


class Carte:

    def __init__(self, rang, couleur):
        if rang not in RANGS:
            raise ValueError(f"Rang inconnu : {rang!r}")
        if not isinstance(couleur, Couleur):
            raise TypeError(f"Enseigne inconnue : {couleur!r}")
        self._rang = rang
        self._couleur = couleur

    @property
    def rang(self):
        return self._rang

    @property
    def couleur(self):
        return self._couleur

    @property
    def valeur_base(self):
        if self.rang == "A":
            return 1
        if self.rang in ("J", "Q", "K"):
            return 10
        return int(self.rang)

    def __eq__(self, other):
        if not isinstance(other, Carte):
            return NotImplemented
        return self.rang == other.rang and self.couleur == other.couleur

    def __hash__(self):
        return hash((self.rang, self.couleur))

    def __repr__(self):
        return f"Carte({self.rang!r}, {self.couleur!r})"


class PaquetEpuise(Exception):
    pass


class Paquet:

    def __init__(self, cartes):
        self._cartes = list(cartes)
        if not all(isinstance(carte, Carte) for carte in self._cartes):
            raise ValueError("Un paquet ne peut contenir que des cartes valides.")
        if len(set(self._cartes)) != len(self._cartes):
            raise ValueError("Un paquet ne peut pas contenir de doublon.")

    @classmethod
    def melange(cls, hasard=None):
        cartes = []
        for couleur in Couleur:
            for rang in RANGS:
                cartes.append(Carte(rang, couleur))
        generator = hasard if hasard is not None else Random()
        generator.shuffle(cartes)
        return cls(cartes)

    def piocher(self):
        if not self._cartes:
            raise PaquetEpuise("Le paquet est épuisé.")
        return self._cartes.pop(0)

    def __len__(self):
        return len(self._cartes)


class Main:

    def __init__(
        self,
        mise,
        cartes=None,
        apres_separation=False,
        as_separes=False,
    ):
        self.mise = mise
        self.cartes = [] if cartes is None else list(cartes)
        self.apres_separation = apres_separation
        self.as_separes = as_separes
        self.terminee = False
        self.doublee = False

    @property
    def score(self):
        total = 0
        a_un_as = False
        for carte in self.cartes:
            total += carte.valeur_base
            if carte.rang == "A":
                a_un_as = True
        if a_un_as and total + 10 <= 21:
            return total + 10, True
        return total, False

    @property
    def valeur(self):
        return self.score[0]

    @property
    def souple(self):
        return self.score[1]

    @property
    def depassee(self):
        return self.valeur > 21

    @property
    def est_blackjack(self):
        return not self.apres_separation and len(self.cartes) == 2 and self.valeur == 21
