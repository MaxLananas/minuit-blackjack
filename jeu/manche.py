from decimal import Decimal, InvalidOperation
from enum import StrEnum

from jeu.cartes import Main, Paquet, PaquetEpuise


class Etat(StrEnum):

    MISE = "mise"
    DISTRIBUTION = "distribution"
    TOUR_JOUEUR = "tour du joueur"
    TOUR_RIVAUX = "tour des rivaux"
    TOUR_CROUPIER = "tour du croupier"
    REGLEMENT = "règlement"
    MANCHE_TERMINEE = "manche terminée"


class ActionImpossible(Exception):
    pass


class SoldeInsuffisant(ActionImpossible):
    pass


def verifier_montant(valeur, *, entier=False):
    try:
        montant = Decimal(str(valeur))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError("Somme invalide.") from error
    if not montant.is_finite() or montant <= 0:
        raise ValueError("La somme doit être strictement positive et finie.")
    if entier and montant != montant.to_integral_value():
        raise ValueError("Les mises doivent être des nombres entiers d'unités.")
    return montant


class ResultatMain:

    def __init__(self, etiquette, mise, paiement, score_joueur, score_croupier):
        self.etiquette = etiquette
        self.mise = mise
        self.paiement = paiement
        self.score_joueur = score_joueur
        self.score_croupier = score_croupier

    @property
    def net(self):
        return self.paiement - self.mise


class BilanManche:

    def __init__(self, numero, mains, annulee=False):
        self.numero = numero
        self.mains = mains
        self.annulee = annulee

    @property
    def mise(self):
        total = Decimal(0)
        for main in self.mains:
            total += main.mise
        return total

    @property
    def paiement(self):
        total = Decimal(0)
        for main in self.mains:
            total += main.paiement
        return total

    @property
    def net(self):
        return self.paiement - self.mise


class Distribution:

    def __init__(self, cible, indice_main, carte, cachee=False):
        self.cible = cible
        self.indice_main = indice_main
        self.carte = carte
        self.cachee = cachee


def actions_possibles(main, nombre_mains, solde):
    if main.terminee or main.valeur >= 21 or len(main.cartes) < 2:
        return set()
    actions = {"tirer", "rester"}
    deux_cartes = len(main.cartes) == 2
    assez_argent = solde >= main.mise
    if deux_cartes and not main.as_separes and assez_argent:
        actions.add("doubler")
    if (
        deux_cartes
        and nombre_mains == 1
        and assez_argent
        and main.cartes[0].rang == main.cartes[1].rang
    ):
        actions.add("separer")
    return actions


class PartieBlackjack:

    def __init__(self, solde_initial=1000, fabrique_paquet=None):
        self.solde_initial = verifier_montant(solde_initial, entier=True)
        self._fabrique_paquet = fabrique_paquet or Paquet.melange
        self.reinitialiser_session()

    def reinitialiser_session(self, solde_initial=None):
        if solde_initial is not None:
            self.solde_initial = verifier_montant(solde_initial, entier=True)
        self.solde = self.solde_initial
        self.mise_en_attente = Decimal(0)
        self.etat = Etat.MISE
        self.mains = []
        self.croupier = Main(Decimal(0))
        self.main_active = 0
        self.croupier_revele = False
        self.historique = []
        self.paquet = None
        self._indice_distribution = 0
        self.derniere_mise = Decimal(0)

    def _verifier_etat(self, etat):
        if self.etat != etat:
            raise ActionImpossible(f"Action indisponible pendant : {self.etat.value}.")

    def miser(self, montant):
        self._verifier_etat(Etat.MISE)
        montant = verifier_montant(montant, entier=True)
        if montant > self.solde:
            raise SoldeInsuffisant("Solde insuffisant pour ce jeton.")
        self.solde -= montant
        self.mise_en_attente += montant

    def effacer_mise(self):
        self._verifier_etat(Etat.MISE)
        self.solde += self.mise_en_attente
        self.mise_en_attente = Decimal(0)

    def commencer_manche(self):
        self._verifier_etat(Etat.MISE)
        if self.mise_en_attente <= 0:
            raise ActionImpossible("Placez une mise avant de distribuer.")
        paquet = self._fabrique_paquet()
        if not isinstance(paquet, Paquet):
            raise TypeError("La fabrique doit renvoyer un paquet.")
        if len(paquet) < 4:
            raise PaquetEpuise("Quatre cartes sont nécessaires pour commencer.")
        self.paquet = paquet
        self.derniere_mise = self.mise_en_attente
        self.mains = [Main(mise=self.mise_en_attente)]
        self.mise_en_attente = Decimal(0)
        self.croupier = Main(Decimal(0))
        self.croupier_revele = False
        self.main_active = 0
        self._indice_distribution = 0
        self.etat = Etat.DISTRIBUTION

    def distribuer_carte(self):
        self._verifier_etat(Etat.DISTRIBUTION)
        carte = self.paquet.piocher()
        cible = "joueur" if self._indice_distribution % 2 == 0 else "croupier"
        cachee = self._indice_distribution == 3
        if cible == "joueur":
            self.mains[0].cartes.append(carte)
        else:
            self.croupier.cartes.append(carte)
        self._indice_distribution += 1
        if self._indice_distribution == 4:
            if self.mains[0].est_blackjack or self.croupier.est_blackjack:
                self.mains[0].terminee = True
                self.etat = Etat.TOUR_CROUPIER
            else:
                self.etat = Etat.TOUR_JOUEUR
        return Distribution(cible, 0, carte, cachee)

    @property
    def cartes_croupier_visibles(self):
        visible = []
        for index, carte in enumerate(self.croupier.cartes):
            if index == 0 or self.croupier_revele:
                visible.append(carte)
            else:
                visible.append(None)
        return tuple(visible)

    @property
    def score_croupier_connu(self):
        visible = [
            carte for carte in self.cartes_croupier_visibles if carte is not None
        ]
        return Main(Decimal(0), cartes=visible).score

    def actions_autorisees(self):
        if self.etat != Etat.TOUR_JOUEUR:
            return set()
        main = self.mains[self.main_active]
        return actions_possibles(main, len(self.mains), self.solde)

    def _verifier_action(self, name):
        self._verifier_etat(Etat.TOUR_JOUEUR)
        if name not in self.actions_autorisees():
            if name in {"doubler", "separer"}:
                main = self.mains[self.main_active]
                if self.solde < main.mise:
                    raise SoldeInsuffisant("Solde insuffisant pour cette action.")
            raise ActionImpossible("Cette action n'est pas autorisée pour cette main.")

    def _passer_main_suivante(self):
        self.mains[self.main_active].terminee = True
        for index in range(self.main_active + 1, len(self.mains)):
            if not self.mains[index].terminee:
                self.main_active = index
                return
        self.etat = Etat.TOUR_CROUPIER

    def _piocher_ou_annuler(self):
        try:
            return self.paquet.piocher()
        except PaquetEpuise:
            self._annuler_manche()
            return None

    def tirer(self):
        self._verifier_action("tirer")
        index = self.main_active
        carte = self._piocher_ou_annuler()
        if carte is None:
            return None
        main = self.mains[index]
        main.cartes.append(carte)
        if main.valeur >= 21:
            self._passer_main_suivante()
        return Distribution("joueur", index, carte)

    def rester(self):
        self._verifier_action("rester")
        self._passer_main_suivante()

    def doubler(self):
        self._verifier_action("doubler")
        index = self.main_active
        carte = self._piocher_ou_annuler()
        if carte is None:
            return None
        main = self.mains[index]
        self.solde -= main.mise
        main.mise *= 2
        main.doublee = True
        main.cartes.append(carte)
        self._passer_main_suivante()
        return Distribution("joueur", index, carte)

    def separer(self):
        self._verifier_action("separer")
        if len(self.paquet) < 2:
            self._annuler_manche()
            return ()
        premiere = self.mains[0]
        seconde_carte = premiere.cartes.pop()
        as_separes = premiere.cartes[0].rang == "A"
        premiere.apres_separation = True
        premiere.as_separes = as_separes
        seconde = Main(
            premiere.mise,
            cartes=[seconde_carte],
            apres_separation=True,
            as_separes=as_separes,
        )
        self.mains.append(seconde)
        self.solde -= premiere.mise
        carte_premiere_main = self.paquet.piocher()
        carte_seconde_main = self.paquet.piocher()
        premiere.cartes.append(carte_premiere_main)
        seconde.cartes.append(carte_seconde_main)
        for main in self.mains:
            main.terminee = as_separes or main.valeur >= 21
        if premiere.terminee:
            if seconde.terminee:
                self.etat = Etat.TOUR_CROUPIER
            else:
                self.main_active = 1
        return (
            Distribution("joueur", 0, carte_premiere_main),
            Distribution("joueur", 1, carte_seconde_main),
        )

    def reveler_croupier(self):
        self._verifier_etat(Etat.TOUR_CROUPIER)
        if self.croupier_revele:
            raise ActionImpossible("La carte du croupier est déjà visible.")
        self.croupier_revele = True
        if not self._croupier_doit_piocher():
            self.etat = Etat.REGLEMENT

    def _croupier_doit_piocher(self):
        if self.croupier.est_blackjack:
            return False
        if not any(not main.depassee and not main.est_blackjack for main in self.mains):
            return False
        return self.croupier.valeur < 17

    def jouer_croupier(self):
        self._verifier_etat(Etat.TOUR_CROUPIER)
        if not self.croupier_revele or not self._croupier_doit_piocher():
            raise ActionImpossible("Le croupier ne peut pas tirer maintenant.")
        carte = self._piocher_ou_annuler()
        if carte is None:
            return None
        self.croupier.cartes.append(carte)
        if not self._croupier_doit_piocher():
            self.etat = Etat.REGLEMENT
        return Distribution("croupier", 0, carte)

    def _calculer_resultat_main(self, main):
        mise = main.mise
        if main.depassee:
            etiquette, paiement = "Dépassé", Decimal(0)
        elif self.croupier.est_blackjack:
            etiquette, paiement = (
                ("Égalité", mise) if main.est_blackjack else ("Perdu", Decimal(0))
            )
        elif main.est_blackjack:
            etiquette, paiement = "Blackjack", mise * Decimal("2.5")
        elif self.croupier.depassee or main.valeur > self.croupier.valeur:
            etiquette, paiement = "Gagné", mise * 2
        elif main.valeur == self.croupier.valeur:
            etiquette, paiement = "Égalité", mise
        else:
            etiquette, paiement = "Perdu", Decimal(0)
        return ResultatMain(
            etiquette, mise, paiement, main.valeur, self.croupier.valeur
        )

    def regler_manche(self):
        self._verifier_etat(Etat.REGLEMENT)
        resultats = tuple(self._calculer_resultat_main(main) for main in self.mains)
        bilan = BilanManche(len(self.historique) + 1, resultats)
        self.solde += bilan.paiement
        self.historique.append(bilan)
        self.etat = Etat.MANCHE_TERMINEE
        return bilan

    def _annuler_manche(self):
        resultats = tuple(
            ResultatMain(
                "Annulée", main.mise, main.mise, main.valeur, self.croupier.valeur
            )
            for main in self.mains
        )
        bilan = BilanManche(len(self.historique) + 1, resultats, annulee=True)
        self.solde += bilan.paiement
        self.historique.append(bilan)
        self.croupier_revele = True
        self.etat = Etat.MANCHE_TERMINEE

    def nouvelle_manche(self, repeter_mise=False):
        self._verifier_etat(Etat.MANCHE_TERMINEE)
        if repeter_mise and self.solde < self.derniere_mise:
            raise SoldeInsuffisant("Solde insuffisant pour répéter la dernière mise.")
        self.etat = Etat.MISE
        self.mains = []
        self.croupier = Main(Decimal(0))
        self.croupier_revele = False
        self.main_active = 0
        self.paquet = None
        if repeter_mise and self.derniere_mise:
            self.miser(self.derniere_mise)
