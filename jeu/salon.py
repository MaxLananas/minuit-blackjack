from decimal import Decimal
from random import Random

from jeu.cartes import Main, Paquet, PaquetEpuise
from jeu.manche import (
    ActionImpossible,
    BilanManche,
    Distribution,
    Etat,
    PartieBlackjack,
    ResultatMain,
    actions_possibles,
)
from jeu.rivaux import choisir_action


class Rival:

    def __init__(self, nom):
        self.nom = nom
        self.solde = Decimal(0)
        self.mains = []
        self.main_active = 0
        self.historique = []
        self.derniere_action = ""
        self.dernier_resultat = None


class SalonBlackjack(PartieBlackjack):

    def __init__(
        self,
        solde_initial=1000,
        fabrique_paquet=None,
        noms_rivaux=("MARC", "LÉA"),
        hasard=None,
    ):
        self.rivaux = [Rival(nom) for nom in noms_rivaux]
        self._hasard_rivaux = hasard or Random()
        super().__init__(solde_initial, fabrique_paquet)

    def reinitialiser_session(self, solde_initial=None):
        super().reinitialiser_session(solde_initial)
        for rival in self.rivaux:
            rival.solde = self.solde_initial
            rival.mains = []
            rival.main_active = 0
            rival.historique = []
            rival.derniere_action = ""
            rival.dernier_resultat = None
        self.rival_actif = 0
        self._ordre_distribution = []

    @property
    def nombre_cartes_depart(self):
        return 2 * len(self._ordre_distribution)

    def commencer_manche(self):
        self._verifier_etat(Etat.MISE)
        if self.mise_en_attente <= 0:
            raise ActionImpossible("Placez une mise avant de distribuer.")
        participants = [i for i, rival in enumerate(self.rivaux) if rival.solde >= 1]
        paquet = self._fabrique_paquet()
        if not isinstance(paquet, Paquet):
            raise TypeError("La fabrique doit renvoyer un paquet.")
        if len(paquet) < 2 * (len(participants) + 2):
            raise PaquetEpuise("Il manque des cartes pour la distribution initiale.")
        self.paquet = paquet
        self.derniere_mise = self.mise_en_attente
        self.mains = [Main(self.mise_en_attente)]
        self.mise_en_attente = Decimal(0)
        self.croupier = Main(Decimal(0))
        self.croupier_revele = False
        self.main_active = 0
        self.rival_actif = 0
        self._indice_distribution = 0
        self._ordre_distribution = (
            ["joueur"] + [f"rival_{i}" for i in participants] + ["croupier"]
        )
        for i, rival in enumerate(self.rivaux):
            rival.mains = []
            rival.main_active = 0
            rival.derniere_action = ""
            rival.dernier_resultat = None
            if i in participants:
                mise = min(
                    self.derniere_mise,
                    Decimal(25),
                    rival.solde.to_integral_value(rounding="ROUND_FLOOR"),
                )
                rival.solde -= mise
                rival.mains = [Main(mise)]
        self.etat = Etat.DISTRIBUTION

    def distribuer_carte(self):
        self._verifier_etat(Etat.DISTRIBUTION)
        places = self._ordre_distribution
        cible = places[self._indice_distribution % len(places)]
        cachee = cible == "croupier" and self._indice_distribution >= len(places)
        carte = self.paquet.piocher()
        if cible == "joueur":
            self.mains[0].cartes.append(carte)
        elif cible == "croupier":
            self.croupier.cartes.append(carte)
        else:
            self.rivaux[int(cible.split("_")[1])].mains[0].cartes.append(carte)
        self._indice_distribution += 1
        if self._indice_distribution == self.nombre_cartes_depart:
            for main in self._toutes_les_mains():
                if main.est_blackjack or self.croupier.est_blackjack:
                    main.terminee = True
            if self.croupier.est_blackjack:
                self.etat = Etat.TOUR_CROUPIER
            elif self.mains[0].terminee:
                self._passer_aux_rivaux()
            else:
                self.etat = Etat.TOUR_JOUEUR
        return Distribution(cible, 0, carte, cachee)

    def _toutes_les_mains(self):
        return self.mains + [main for rival in self.rivaux for main in rival.mains]

    def _passer_aux_rivaux(self):
        for index, rival in enumerate(self.rivaux):
            for indice_main, main in enumerate(rival.mains):
                if not main.terminee:
                    self.rival_actif = index
                    rival.main_active = indice_main
                    self.etat = Etat.TOUR_RIVAUX
                    return
        self.etat = Etat.TOUR_CROUPIER

    def _passer_main_suivante(self):
        super()._passer_main_suivante()
        if self.etat == Etat.TOUR_CROUPIER:
            self._passer_aux_rivaux()

    def separer(self):
        deals = super().separer()
        if self.etat == Etat.TOUR_CROUPIER:
            self._passer_aux_rivaux()
        return deals

    def actions_rival_possibles(self):
        if self.etat != Etat.TOUR_RIVAUX:
            return set()
        rival = self.rivaux[self.rival_actif]
        main = rival.mains[rival.main_active]
        return actions_possibles(main, len(rival.mains), rival.solde)

    @property
    def cartes_visibles(self):
        visible = []
        for main in self._toutes_les_mains():
            visible.extend(main.cartes)
        for carte in self.cartes_croupier_visibles:
            if carte is not None:
                visible.append(carte)
        return tuple(visible)

    def choisir_action_rival(self, difficulte):
        self._verifier_etat(Etat.TOUR_RIVAUX)
        rival = self.rivaux[self.rival_actif]
        return choisir_action(
            rival.mains[rival.main_active],
            self.cartes_croupier_visibles[0],
            self.cartes_visibles,
            self.actions_rival_possibles(),
            difficulte,
            self._hasard_rivaux,
        )

    def _passer_rival_suivant(self):
        rival = self.rivaux[self.rival_actif]
        rival.mains[rival.main_active].terminee = True
        self._passer_aux_rivaux()

    def faire_jouer_rival(self, action):
        self._verifier_etat(Etat.TOUR_RIVAUX)
        if action not in self.actions_rival_possibles():
            raise ActionImpossible("Action adverse non autorisée.")
        indice_rival = self.rival_actif
        rival = self.rivaux[indice_rival]
        indice_main = rival.main_active
        main = rival.mains[indice_main]
        cible = f"rival_{indice_rival}"
        rival.derniere_action = action
        if action == "rester":
            self._passer_rival_suivant()
            return ()
        if action == "separer":
            if len(self.paquet) < 2:
                self._annuler_manche()
                return ()
            seconde_carte = main.cartes.pop()
            as_separes = main.cartes[0].rang == "A"
            main.apres_separation = True
            main.as_separes = as_separes
            seconde = Main(
                main.mise,
                cartes=[seconde_carte],
                apres_separation=True,
                as_separes=as_separes,
            )
            rival.mains.append(seconde)
            rival.solde -= main.mise
            tirages = (self.paquet.piocher(), self.paquet.piocher())
            main.cartes.append(tirages[0])
            seconde.cartes.append(tirages[1])
            for piece in rival.mains:
                piece.terminee = as_separes or piece.valeur >= 21
            if main.terminee:
                self._passer_aux_rivaux()
            return tuple(
                Distribution(cible, index, carte) for index, carte in enumerate(tirages)
            )
        carte = self._piocher_ou_annuler()
        if carte is None:
            return ()
        if action == "doubler":
            rival.solde -= main.mise
            main.mise *= 2
            main.doublee = True
        main.cartes.append(carte)
        if action == "doubler" or main.valeur >= 21:
            self._passer_rival_suivant()
        return (Distribution(cible, indice_main, carte),)

    def _croupier_doit_piocher(self):
        if self.croupier.est_blackjack:
            return False
        if not any(
            not main.depassee and not main.est_blackjack
            for main in self._toutes_les_mains()
        ):
            return False
        return self.croupier.valeur < 17

    def regler_manche(self):
        self._verifier_etat(Etat.REGLEMENT)
        resultats = []
        for rival in self.rivaux:
            if not rival.mains:
                resultats.append(None)
                continue
            mains = []
            for main in rival.mains:
                mains.append(self._calculer_resultat_main(main))
            resultats.append(BilanManche(len(self.historique) + 1, tuple(mains)))
        bilan = super().regler_manche()
        for rival, resultat in zip(self.rivaux, resultats):
            if resultat is not None:
                rival.solde += resultat.paiement
                rival.dernier_resultat = resultat
                rival.historique.append(resultat)
        return bilan

    def _annuler_manche(self):
        for rival in self.rivaux:
            if rival.mains:
                resultats = tuple(
                    ResultatMain(
                        "Annulée",
                        main.mise,
                        main.mise,
                        main.valeur,
                        self.croupier.valeur,
                    )
                    for main in rival.mains
                )
                bilan = BilanManche(len(self.historique) + 1, resultats, annulee=True)
                rival.solde += bilan.paiement
                rival.dernier_resultat = bilan
                rival.historique.append(bilan)
        super()._annuler_manche()

    def nouvelle_manche(self, repeter_mise=False):
        super().nouvelle_manche(repeter_mise)
        for rival in self.rivaux:
            rival.mains = []
            rival.derniere_action = ""
            rival.dernier_resultat = None
        self._ordre_distribution = []
