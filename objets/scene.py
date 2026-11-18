from ursina import Entity, Vec3

from jeu.cartes import Carte, Couleur
from jeu.manche import Etat
from objets.cartes import Carte3D
from objets.jetons import PilesJetons
from objets.personnages import Personnages
from objets.ressources import modele
from objets.table import TableCasino


class SceneTable:

    def __init__(self, resources):
        self.resources = resources
        self.table = TableCasino(resources)
        self.people = Personnages()
        self.chips = PilesJetons(resources)
        self.player_cards = {}
        self.opponent_cards = {}
        self.dealer_cards = {}
        self.demo_cards = []
        self.active_frame = Entity(
            model=modele("plan"),
            y=0.071,
            scale=(3.4, 1, 2.0),
            texture=resources.texture("images/main-active.png"),
            double_sided=True,
            unlit=True,
            enabled=False,
        )
        self.show_demo()

    def show_demo(self):
        self.clear_cards()
        self.active_frame.enabled = False
        self.demo_cards = [
            Carte3D(
                self.resources, Carte("A", Couleur.PIQUE), position=(-0.7, 0.14, -1.1)
            ),
            Carte3D(
                self.resources, Carte("K", Couleur.COEUR), position=(0.7, 0.14, -1.1)
            ),
        ]
        self.chips.display([(125, 2.0, -2.1)])

    def clear_cards(self):
        for view in (
            list(self.player_cards.values())
            + list(self.opponent_cards.values())
            + list(self.dealer_cards.values())
            + self.demo_cards
        ):
            view.destroy()
        self.player_cards.clear()
        self.opponent_cards.clear()
        self.dealer_cards.clear()
        self.demo_cards.clear()

    def _positions(self, count, center_x, z, max_width, spacing=1.1):
        spacing = min(spacing, max_width / max(1, count - 1))
        return [
            Vec3(
                center_x + (index - (count - 1) / 2) * spacing, 0.14 + index * 0.004, z
            )
            for index in range(count)
        ]

    def sync(self, partie, animate_new=False):
        if self.demo_cards:
            self.clear_cards()
        movements = []
        live_player = set()
        split = len(partie.mains) == 2
        for indice_main, main in enumerate(partie.mains):
            center = (-1.5 if indice_main == 0 else 1.5) if split else 0
            positions = self._positions(
                len(main.cartes), center, -1.45, 1.7 if split else 4.2
            )
            for carte, cible in zip(main.cartes, positions):
                live_player.add(carte)
                if carte not in self.player_cards:
                    start = Vec3(4.35, 0.48, 1.75) if animate_new else cible
                    self.player_cards[carte] = Carte3D(
                        self.resources, carte, position=start
                    )
                    self.player_cards[carte].root.scale = 0.88
                view = self.player_cards[carte]
                movements.append((view.root, Vec3(view.root.position), cible))
        for carte in set(self.player_cards) - live_player:
            self.player_cards.pop(carte).destroy()
        live_opponents = set()
        for indice_rival, rival in enumerate(partie.rivaux):
            side = -1 if indice_rival == 0 else 1
            for indice_main, main in enumerate(rival.mains):
                center = side * 3.85 + (
                    (-0.7 if indice_main == 0 else 0.7) if len(rival.mains) > 1 else 0
                )
                positions = self._positions(
                    len(main.cartes), center, 0.12,
                    0.55 if len(rival.mains) > 1 else 1.45, spacing=0.60
                )
                for carte, cible in zip(main.cartes, positions):
                    key = (indice_rival, carte)
                    live_opponents.add(key)
                    if key not in self.opponent_cards:
                        start = Vec3(4.35, 0.48, 1.75) if animate_new else cible
                        self.opponent_cards[key] = Carte3D(
                            self.resources, carte, position=start
                        )
                        self.opponent_cards[key].root.scale = 0.67
                    view = self.opponent_cards[key]
                    movements.append((view.root, Vec3(view.root.position), cible))
        for key in set(self.opponent_cards) - live_opponents:
            self.opponent_cards.pop(key).destroy()
        visible = partie.cartes_croupier_visibles
        positions = self._positions(len(visible), 0, 1.35, 3.7, spacing=0.95)
        for index, (carte, cible) in enumerate(zip(visible, positions)):
            if index not in self.dealer_cards:
                start = Vec3(4.35, 0.48, 1.75) if animate_new else cible
                self.dealer_cards[index] = Carte3D(
                    self.resources, carte, cachee=carte is None, position=start
                )
                self.dealer_cards[index].root.scale = 0.8
            view = self.dealer_cards[index]
            if carte is not None and view.cachee:
                view.reveal(carte)
                view.pivot.rotation_z = 0
            movements.append((view.root, Vec3(view.root.position), cible))
        for index in set(self.dealer_cards) - set(range(len(visible))):
            self.dealer_cards.pop(index).destroy()
        self.active_frame.enabled = partie.etat == Etat.TOUR_JOUEUR
        if self.active_frame.enabled:
            self.active_frame.x = (
                (-1.5 if partie.main_active == 0 else 1.5) if split else 0
            )
            self.active_frame.z = -1.45
            self.active_frame.scale_x = 2.85 if split else 3.6
        if partie.etat == Etat.MISE:
            amounts = (
                [(partie.mise_en_attente, 0, -2.65)] if partie.mise_en_attente else []
            )
        else:
            amounts = [
                (main.mise, (-1.5 if i == 0 else 1.5) if split else 0, -2.65)
                for i, main in enumerate(partie.mains)
            ]
            for indice_rival, rival in enumerate(partie.rivaux):
                side = -1 if indice_rival == 0 else 1
                for i, main in enumerate(rival.mains):
                    offset = (-0.7 if i == 0 else 0.7) if len(rival.mains) > 1 else 0
                    amounts.append((main.mise, side * 3.85 + offset, -0.8))
        self.chips.display(amounts)
        if not animate_new:
            for entity, _, cible in movements:
                entity.position = cible
        return movements

    def prepare_reveal(self, partie):
        if len(partie.cartes_croupier_visibles) < 2 or 1 not in self.dealer_cards:
            return None
        view = self.dealer_cards[1]
        carte = partie.cartes_croupier_visibles[1]
        if carte is not None and view.cachee:
            view.reveal(carte)
            return view
        return None
