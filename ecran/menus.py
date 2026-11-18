from decimal import Decimal

from ursina import Button, Entity, camera, color
from ursina.prefabs.input_field import InputField

from ecran.boutons import (
    BUTTON,
    CREAM,
    DARK,
    EDGE,
    GOLD,
    MUTED,
    SANS,
    SANS_BOLD,
    BoutonCasino,
    etiquette,
    line,
    panel,
)
from ecran.infos import amount_text, round_message
from ecran.tuto import tutorial_step
from jeu.manche import Etat
from objets.ressources import modele


class InterfaceJeu:

    def __init__(self, controller):
        self.controller = controller
        self.menu = Entity(parent=camera.ui, name="menu_principal")
        self.hud = Entity(parent=camera.ui, name="interface_partie", enabled=False)
        self.pause = Entity(parent=camera.ui, name="pause", enabled=False, z=-0.3)
        self.settings = Entity(
            parent=camera.ui, name="parametres", enabled=False, z=-0.4
        )
        self.historique = Entity(
            parent=camera.ui, name="historique", enabled=False, z=-0.3
        )
        self.confirm = Entity(
            parent=camera.ui, name="confirmation", enabled=False, z=-0.5
        )
        self.menu_index = 0
        self._build_menu()
        self._build_hud()
        self._build_pause()
        self._build_settings()
        self._build_history()
        self._build_confirm()

    def _button(self, parent, text, x, y, width, height, callback, **kwargs):
        return BoutonCasino(parent, text, (x, y), (width, height), callback, **kwargs)

    def _build_menu(self):
        root = self.menu
        Entity(
            parent=root,
            model=modele("panneau"),
            position=(-0.53, 0.0, 0.01),
            scale=(0.72, 1.0),
            texture=self.controller.resources.texture("images/ombre-menu.png"),
            color=color.white,
        )
        etiquette(root, "MINUIT", (-0.81, 0.429), 1.25, CREAM, SANS_BOLD)
        etiquette(root, "BLACKJACK  /  SALON", (-0.81, 0.390), 0.62, MUTED, SANS_BOLD)
        line(root, (-0.695, 0.364), (0.23, 0.001), color.rgba32(188, 160, 120, 100))
        callbacks = [
            self.controller.enter_game,
            self.controller.start_tutorial,
            self.controller.open_settings,
            self.controller.quit_game,
        ]
        names = ["JOUER", "APPRENDRE", "PARAMÈTRES", "QUITTER"]
        self.menu_labels = []
        self.menu_buttons = []
        for index, (name, callback) in enumerate(zip(names, callbacks)):
            y = 0.292 - index * 0.069
            text = etiquette(root, name, (-0.774, y), 1.01, CREAM, SANS_BOLD)
            self.menu_labels.append(text)
            button = Button(
                parent=root,
                model=modele("panneau"),
                position=(-0.66, y, -0.04),
                scale=(0.31, 0.05),
                color=color.rgba32(0, 0, 0, 0),
                highlight_color=color.rgba32(0, 0, 0, 0),
                pressed_color=color.rgba32(0, 0, 0, 0),
                highlight_scale=1,
                pressed_scale=1,
            )
            button.on_click = callback
            button.on_mouse_enter = lambda i=index: self.select_menu(i)
            self.menu_buttons.append(button)
        self.menu_play = self.menu_labels[0]
        self.pointer = Entity(
            parent=root,
            model=modele("fleche"),
            position=(-0.803, 0.292, -0.05),
            color=color.rgb32(177, 61, 46),
            double_sided=True,
        )
        etiquette(root, "LA TABLE VOUS ATTEND", (-0.81, -0.115), 0.65, GOLD, SANS_BOLD)
        line(root, (-0.68, -0.14), (0.26, 0.001), color.rgba32(189, 157, 112, 130))
        etiquette(
            root,
            "Deux rivaux à battre. Une banque à plumer.\nÀ toi de jouer tes cartes.",
            (-0.81, -0.178),
            0.68,
            CREAM,
            SANS,
        )
        panel(
            root, (0, -0.466), (1.80, 0.068), color.rgba32(16, 15, 15, 250), depth=-0.02
        )
        etiquette(
            root,
            "BLACKJACK EN JETONS VIRTUELS · AUCUNE MISE RÉELLE",
            (-0.81, -0.466),
            0.57,
            GOLD,
            SANS_BOLD,
            depth=-0.05,
        )
        etiquette(
            root,
            "HAUT / BAS  CHOISIR     ENTRÉE  VALIDER",
            (0.81, -0.466),
            0.57,
            CREAM,
            SANS_BOLD,
            origin=(0.5, 0.5),
            depth=-0.05,
        )
        self.select_menu(0)

    def select_menu(self, index):
        self.menu_index = index % len(self.menu_labels)
        self.pointer.y = 0.292 - self.menu_index * 0.069
        for i, text in enumerate(self.menu_labels):
            text.color = CREAM if i == self.menu_index else MUTED

    def activate_menu(self):
        self.menu_buttons[self.menu_index].on_click()

    def _build_hud(self):
        root = self.hud
        panel(root, (0, 0.458), (1.8, 0.084), color.rgba32(17, 17, 16, 241))
        line(root, (0, 0.415), (1.76, 0.001), EDGE)
        etiquette(root, "MINUIT / 21", (-0.825, 0.47), 0.82, CREAM, SANS_BOLD)
        etiquette(root, "TES JETONS", (-0.825, 0.441), 0.55, MUTED, SANS)
        self.solde = etiquette(root, "1 000", (-0.655, 0.441), 0.83, GOLD, SANS_BOLD)
        self.title = etiquette(
            root, "", (-0.13, 0.475), 0.92, CREAM, SANS_BOLD, origin=(0, 0.5)
        )
        self.subtitle = etiquette(
            root, "", (-0.13, 0.442), 0.62, MUTED, SANS, origin=(0, 0.5)
        )
        self._button(
            root,
            "HISTORIQUE",
            0.54,
            0.46,
            0.17,
            0.048,
            self.controller.open_history,
            shape="panneau",
            text_size=0.59,
        )
        self._button(
            root,
            "PAUSE",
            0.75,
            0.46,
            0.15,
            0.048,
            self.controller.toggle_pause,
            shape="panneau",
            text_size=0.66,
        )
        self.notice = etiquette(
            root, "", (0, 0.376), 0.67, GOLD, SANS_BOLD, origin=(0, 0.5)
        )
        panel(root, (-0.75, 0.155), (0.25, 0.095), color.rgba32(21, 21, 19, 211))
        panel(root, (0.75, 0.155), (0.25, 0.095), color.rgba32(21, 21, 19, 211))
        self.noms_rivaux = []
        self.opponent_details = []
        for x in (-0.855, 0.645):
            self.noms_rivaux.append(
                etiquette(root, "", (x, 0.177), 0.73, CREAM, SANS_BOLD)
            )
            self.opponent_details.append(
                etiquette(root, "", (x, 0.14), 0.63, MUTED, SANS)
            )
        panel(root, (0.75, -0.015), (0.25, 0.22), color.rgba32(21, 21, 19, 211))
        etiquette(root, "LA BANQUE", (0.645, 0.057), 0.60, MUTED, SANS_BOLD)
        self.dealer_score = etiquette(root, "—", (0.645, 0.029), 0.93, CREAM, SANS_BOLD)
        self.dealer_detail = etiquette(root, "", (0.645, 0.000), 0.57, GOLD, SANS)
        line(root, (0.75, -0.025), (0.20, 0.001), EDGE)
        etiquette(root, "TA MAIN", (0.645, -0.052), 0.60, MUTED, SANS_BOLD)
        self.player_score = etiquette(
            root, "—", (0.645, -0.079), 0.92, CREAM, SANS_BOLD
        )
        self.player_detail = etiquette(root, "", (0.645, -0.105), 0.55, GOLD, SANS)
        panel(root, (0, -0.431), (1.8, 0.138), color.rgba32(17, 17, 16, 248))
        line(root, (0, -0.361), (1.76, 0.001), EDGE)
        etiquette(root, "MISE", (-0.835, -0.391), 0.60, MUTED, SANS_BOLD)
        self.bet = etiquette(root, "0", (-0.835, -0.432), 1.12, CREAM, SANS_BOLD)
        etiquette(root, "UNITÉS", (-0.835, -0.47), 0.52, MUTED, SANS)
        line(root, (-0.57, -0.43), (0.001, 0.085), EDGE)
        self.betting = Entity(parent=root)
        self.chip_buttons = {}
        for index, valeur in enumerate((1, 5, 25, 100, 500)):
            button = self._button(
                self.betting,
                str(valeur),
                -0.47 + index * 0.12,
                -0.429,
                0.084,
                0.084,
                lambda v=valeur: self.controller.add_chip(v),
                shape="panneau",
                base_color=color.white,
                text_size=0.6,
            )
            button.texture = self.controller.resources.texture(
                f"images/jeton_{valeur}.png"
            )
            button.normal_color = color.white
            button.hover_color = color.rgb32(255, 235, 196)
            button.down_color = color.rgb32(189, 176, 155)
            button.text_entity.enabled = False
            self.chip_buttons[valeur] = button
        self.clear_button = self._button(
            self.betting,
            "EFFACER",
            0.25,
            -0.429,
            0.16,
            0.058,
            self.controller.effacer_mise,
            shape="panneau",
            text_size=0.64,
        )
        self.deal_button = self._button(
            self.betting,
            "DISTRIBUER",
            0.53,
            -0.429,
            0.30,
            0.064,
            self.controller.deal,
            shape="panneau",
            primary=True,
            text_size=0.72,
        )
        self.actions = Entity(parent=root, enabled=False)
        self.action_buttons = {}
        for index, (title, name) in enumerate(
            (
                ("TIRER", "tirer"),
                ("RESTER", "rester"),
                ("DOUBLER", "doubler"),
                ("SÉPARER", "separer"),
            )
        ):
            self.action_buttons[name] = self._button(
                self.actions,
                title,
                -0.40 + index * 0.27,
                -0.429,
                0.235,
                0.064,
                lambda action=name: self.controller.player_action(action),
                shape="panneau",
                primary=index == 0,
                text_size=0.72,
            )
        self.resultat = Entity(parent=root, enabled=False)
        self.result_detail = etiquette(
            self.resultat, "", (-0.51, -0.396), 0.62, MUTED, SANS
        )
        self.next_button = self._button(
            self.resultat,
            "NOUVELLE MISE",
            0.10,
            -0.44,
            0.26,
            0.06,
            self.controller.nouvelle_manche,
            shape="panneau",
            text_size=0.64,
        )
        self.replay_button = self._button(
            self.resultat,
            "REJOUER LA MISE",
            0.50,
            -0.44,
            0.35,
            0.064,
            self.controller.replay,
            shape="panneau",
            primary=True,
            text_size=0.67,
        )
        self.tutorial = Entity(parent=root, enabled=False)
        panel(
            self.tutorial,
            (-0.58, -0.245),
            (0.54, 0.27),
            color.rgba32(24, 23, 21, 240),
            depth=-0.09,
        )
        line(self.tutorial, (-0.58, -0.12), (0.52, 0.002), GOLD, depth=-0.1)
        self.tutorial_title = etiquette(
            self.tutorial, "", (-0.82, -0.15), 0.62, GOLD, SANS_BOLD, depth=-0.11
        )
        self.tutorial_body = etiquette(
            self.tutorial, "", (-0.82, -0.185), 0.56, CREAM, SANS, depth=-0.11
        )
        self.tutorial_close = self._button(
            self.tutorial,
            "FERMER L'AIDE",
            -0.58,
            -0.355,
            0.26,
            0.039,
            self.controller.end_tutorial,
            shape="panneau",
            text_size=0.57,
        )
        self.tutorial_close.z = -0.12
        self.tutorial_focus = Entity(parent=self.tutorial, enabled=False)
        self.tutorial_focus_edges = [
            panel(self.tutorial_focus, (0, 0), (1, 0.006), GOLD, depth=-0.08)
            for _ in range(2)
        ] + [
            panel(self.tutorial_focus, (0, 0), (0.006, 1), GOLD, depth=-0.08)
            for _ in range(2)
        ]

    def _backdrop(self, root, title, subtitle):
        fond = panel(root, (0, 0), (1.8, 1.02), color.rgba32(8, 8, 8, 218), depth=0)
        fond.collider = "box"
        panel(root, (0, 0), (0.76, 0.76), color.rgba32(28, 26, 24, 250), depth=-0.01)
        line(root, (0, 0.378), (0.76, 0.002), EDGE, depth=-0.02)
        etiquette(
            root, title, (0, 0.30), 1.65, CREAM, SANS_BOLD, origin=(0, 0.5), depth=-0.04
        )
        etiquette(
            root, subtitle, (0, 0.245), 0.62, GOLD, SANS, origin=(0, 0.5), depth=-0.04
        )

    def _build_pause(self):
        root = self.pause
        self._backdrop(root, "PAUSE", "FAIS UNE PAUSE")
        for y, title, callback, primary in (
            (0.153, "REPRENDRE", self.controller.toggle_pause, True),
            (0.078, "PARAMÈTRES", self.controller.open_settings, False),
            (0.003, "APPRENDRE", self.controller.tutorial_from_pause, False),
            (-0.072, "RECOMMENCER LA SESSION", self.controller.ask_reset, False),
            (-0.147, "MENU PRINCIPAL", self.controller.return_to_menu, False),
            (-0.222, "QUITTER", self.controller.quit_game, False),
        ):
            self._button(
                root,
                title,
                0,
                y,
                0.46,
                0.055,
                callback,
                shape="panneau",
                primary=primary,
                text_size=0.65,
            )
        etiquette(
            root,
            "ÉCHAP  POUR REPRENDRE",
            (0, -0.32),
            0.55,
            MUTED,
            SANS,
            origin=(0, 0.5),
        )

    def _build_settings(self):
        root = self.settings
        self._backdrop(root, "RÉGLAGES", "TA TABLE, TES RÈGLES")
        etiquette(root, "JETONS DE DÉPART", (-0.30, 0.18), 0.68, CREAM, SANS_BOLD)
        etiquette(
            root, "Tu auras ce solde à ta prochaine session.",
            (-0.30, 0.148),
            0.55,
            MUTED,
            SANS,
        )
        self.balance_options = {}
        for index, valeur in enumerate((500, 1000, 2500)):
            self.balance_options[valeur] = self._button(
                root,
                amount_text(valeur),
                -0.18 + index * 0.18,
                0.092,
                0.15,
                0.048,
                lambda selected=valeur: self.controller.select_initial_balance(
                    selected
                ),
                shape="panneau",
                text_size=0.64,
            )
        etiquette(
            root,
            "OU CHOISIS TON MONTANT",
            (-0.30, 0.045),
            0.56,
            GOLD,
            SANS_BOLD,
        )
        self.balance_input = InputField(
            parent=root,
            default_value=str(self.controller.solde_initial),
            position=(-0.04, -0.012, -0.04),
            scale=(0.22, 0.05),
            character_limit=7,
            limit_content_to="0123456789",
            color=BUTTON,
            text_color=CREAM,
            text_size=0.65,
        )
        self.balance_input.text_field.text_entity.font = SANS_BOLD
        self.balance_input.submit_on = ["enter"]
        self.balance_input.on_submit = self.controller.apply_custom_balance
        self._button(
            root,
            "OK",
            0.24,
            -0.012,
            0.13,
            0.048,
            self.controller.apply_custom_balance,
            shape="panneau",
            primary=True,
            text_size=0.61,
        )
        self.balance_feedback = etiquette(
            root,
            "De 1 à 1 000 000 jetons.",
            (-0.30, -0.047),
            0.55,
            MUTED,
            SANS,
        )
        line(root, (0, -0.075), (0.59, 0.001), EDGE)
        etiquette(root, "NIVEAU DES RIVAUX", (-0.30, -0.096), 0.68, CREAM, SANS_BOLD)
        self.difficulty_options = {}
        for index, (valeur, title) in enumerate(
            (("facile", "FACILE"), ("normal", "NORMAL"), ("expert", "EXPERT"))
        ):
            self.difficulty_options[valeur] = self._button(
                root,
                title,
                -0.19 + index * 0.19,
                -0.145,
                0.16,
                0.048,
                lambda selected=valeur: self.controller.select_difficulty(selected),
                shape="panneau",
                text_size=0.63,
            )
        etiquette(
            root,
            "La banque s'arrête toujours à 17.",
            (-0.30, -0.181),
            0.55,
            MUTED,
            SANS,
        )
        line(root, (0, -0.207), (0.59, 0.001), EDGE)
        etiquette(root, "SONS DE LA TABLE", (-0.30, -0.232), 0.68, CREAM, SANS_BOLD)
        self.sound_button = self._button(
            root,
            "ACTIVÉS",
            0.20,
            -0.232,
            0.16,
            0.048,
            self.controller.toggle_sound,
            shape="panneau",
            text_size=0.63,
        )
        self._button(
            root,
            "RETOUR À LA TABLE",
            0,
            -0.33,
            0.38,
            0.06,
            self.controller.close_settings,
            shape="panneau",
            primary=True,
            text_size=0.7,
        )

    def _build_history(self):
        root = self.historique
        self._backdrop(root, "HISTORIQUE", "TES SIX DERNIÈRES MANCHES")
        for title, x in (
            ("N°", -0.29),
            ("RÉSULTAT", -0.21),
            ("MISE", 0.09),
            ("NET", 0.25),
        ):
            etiquette(root, title, (x, 0.18), 0.58, GOLD, SANS_BOLD)
        line(root, (0, 0.15), (0.60, 0.001), EDGE)
        self.history_rows = []
        for index in range(6):
            y = 0.12 - index * 0.049
            self.history_rows.append(
                tuple(
                    etiquette(root, "", (x, y), 0.63, CREAM, SANS)
                    for x in (-0.29, -0.21, 0.09, 0.25)
                )
            )
        self.history_empty = etiquette(
            root,
            "Pas encore de manche à raconter.",
            (0, 0.05),
            0.68,
            MUTED,
            SANS,
            origin=(0, 0.5),
        )
        self._button(
            root,
            "RETOUR À LA TABLE",
            0,
            -0.262,
            0.38,
            0.06,
            self.controller.close_history,
            shape="panneau",
            primary=True,
            text_size=0.65,
        )

    def _build_confirm(self):
        root = self.confirm
        self._backdrop(
            root, "ON REPART À ZÉRO ?", "TA SESSION VA ÊTRE RÉINITIALISÉE"
        )
        etiquette(
            root,
            "La manche en cours sera perdue, ainsi que ton historique.\nTu ne pourras pas annuler cette action.",
            (0, 0.105),
            0.72,
            CREAM,
            SANS,
            origin=(0, 0.5),
        )
        self._button(
            root,
            "ANNULER",
            -0.13,
            -0.09,
            0.23,
            0.06,
            self.controller.cancel_reset,
            shape="panneau",
            text_size=0.66,
        )
        self._button(
            root,
            "RECOMMENCER",
            0.13,
            -0.09,
            0.23,
            0.06,
            self.controller.reinitialiser_session,
            shape="panneau",
            primary=True,
            text_size=0.63,
        )

    def show_menu(self, has_session):
        self.menu.enabled = True
        self.hud.enabled = False
        self.pause.enabled = False
        self.historique.enabled = False
        self.confirm.enabled = False
        self.settings.enabled = False
        self.menu_play.text = "REPRENDRE" if has_session else "JOUER"

    def show_game(self):
        self.menu.enabled = False
        self.hud.enabled = True
        self.pause.enabled = False
        self.historique.enabled = False
        self.confirm.enabled = False
        self.settings.enabled = False

    def refresh_settings(self):
        for options, current in (
            (self.balance_options, self.controller.solde_initial),
            (self.difficulty_options, self.controller.difficulte),
        ):
            for valeur, button in options.items():
                selected = valeur == current
                button.normal_color = GOLD if selected else BUTTON
                button.normal_text = DARK if selected else CREAM
                button.hover_color = (
                    color.rgb32(241, 200, 137) if selected else color.rgb32(89, 69, 53)
                )
                button.down_color = (
                    color.rgb32(180, 133, 74) if selected else color.rgb32(38, 33, 29)
                )
                button.set_available(True)
        self.sound_button.text = (
            "ACTIVÉS" if self.controller.sound.enabled else "COUPÉS"
        )

    def refresh_history(self, partie):
        records = list(reversed(partie.historique[-6:]))
        self.history_empty.enabled = not records
        for index, row in enumerate(self.history_rows):
            if index >= len(records):
                for text in row:
                    text.text = ""
                continue
            bilan = records[index]
            resultats = " / ".join(main.etiquette for main in bilan.mains)
            for text, valeur in zip(
                row,
                (
                    str(bilan.numero),
                    resultats,
                    amount_text(bilan.mise),
                    amount_text(bilan.net, signed=True),
                ),
            ):
                text.text = valeur
            row[3].color = GOLD if bilan.net > 0 else CREAM

    def refresh(self, partie, busy=False, notice=""):
        self.solde.text = amount_text(partie.solde)
        mise = (
            partie.mise_en_attente
            if partie.etat == Etat.MISE
            else sum((main.mise for main in partie.mains), Decimal(0))
        )
        self.bet.text = amount_text(mise)
        self.notice.text = notice
        dealer_cards = partie.cartes_croupier_visibles
        if dealer_cards:
            self.dealer_score.text = str(partie.score_croupier_connu[0]) + (
                " + ?" if None in dealer_cards else ""
            )
            self.dealer_detail.text = (
                "carte cachée" if None in dealer_cards else "main révélée"
            )
            if partie.etat == Etat.DISTRIBUTION and None not in dealer_cards:
                self.dealer_detail.text = "distribution"
        else:
            self.dealer_score.text = "—"
            self.dealer_detail.text = "en attente"
        if partie.mains and partie.mains[partie.main_active].cartes:
            main = partie.mains[partie.main_active]
            self.player_score.text = str(main.valeur)
            if len(partie.mains) == 2:
                values = [
                    str(current.valeur) + ("*" if index == partie.main_active else "")
                    for index, current in enumerate(partie.mains)
                ]
                self.player_detail.text = f"M1 {values[0]}  ·  M2 {values[1]}"
            else:
                self.player_detail.text = "main souple" if main.souple else "main 1 / 1"
        else:
            self.player_score.text = "—"
            self.player_detail.text = "en attente"
        action_names = {
            "tirer": "tire",
            "rester": "reste",
            "doubler": "double",
            "separer": "sépare",
        }
        for index, rival in enumerate(partie.rivaux):
            if rival.mains and rival.mains[0].cartes:
                scores = "/".join(str(main.valeur) for main in rival.mains)
                action = action_names.get(rival.derniere_action, "")
                resultat = (
                    " / ".join(r.etiquette for r in rival.dernier_resultat.mains)
                    if rival.dernier_resultat
                    else action
                )
                self.noms_rivaux[index].text = f"{rival.nom}  •  {scores}"
                self.opponent_details[
                    index
                ].text = f"{amount_text(rival.solde)}  {resultat}"
            else:
                self.noms_rivaux[index].text = rival.nom
                self.opponent_details[index].text = (
                    f"Solde {amount_text(rival.solde)}"
                    if rival.solde >= 1
                    else "En retrait"
                )
        etat = partie.etat
        self.betting.enabled = etat == Etat.MISE
        self.actions.enabled = etat in {
            Etat.DISTRIBUTION,
            Etat.TOUR_JOUEUR,
            Etat.TOUR_RIVAUX,
            Etat.TOUR_CROUPIER,
            Etat.REGLEMENT,
        }
        self.resultat.enabled = etat == Etat.MANCHE_TERMINEE
        for valeur, button in self.chip_buttons.items():
            button.set_available(
                not busy and etat == Etat.MISE and partie.solde >= valeur
            )
        self.clear_button.set_available(
            not busy and etat == Etat.MISE and partie.mise_en_attente > 0
        )
        self.deal_button.set_available(
            not busy and etat == Etat.MISE and partie.mise_en_attente > 0
        )
        autorisees = partie.actions_autorisees() if not busy else set()
        for name, button in self.action_buttons.items():
            button.set_available(name in autorisees)
        self.next_button.set_available(not busy)
        self.replay_button.set_available(
            not busy and partie.solde >= partie.derniere_mise
        )
        titles = {
            Etat.MISE: ("À TOI DE MISER", "Ajoute des jetons, puis lance la manche."),
            Etat.DISTRIBUTION: ("LES CARTES ARRIVENT", "Deux cartes pour chaque joueur."),
            Etat.TOUR_JOUEUR: ("À TOI DE JOUER", "Vise 21 sans dépasser."),
            Etat.TOUR_RIVAUX: (
                f"{partie.rivaux[partie.rival_actif].nom} JOUE"
                if partie.rivaux
                else "LES RIVAUX JOUENT",
                "Chacun tente de battre la banque.",
            ),
            Etat.TOUR_CROUPIER: ("LA BANQUE JOUE", "Elle tire jusqu'à 17, puis s'arrête."),
            Etat.REGLEMENT: ("VERDICT", "On compare les mains."),
        }
        if etat in titles:
            self.title.text, self.subtitle.text = titles[etat]
        elif partie.historique:
            bilan = partie.historique[-1]
            self.title.text, self.subtitle.text = round_message(bilan)
            self.result_detail.text = "   ·   ".join(
                f"Main {index + 1} : {resultat.etiquette} ({amount_text(resultat.net, signed=True)})"
                for index, resultat in enumerate(bilan.mains)
            )
        self.tutorial.enabled = self.controller.tutorial_active
        if self.tutorial.enabled:
            titre, texte, cible = tutorial_step(partie)
            self.tutorial_title.text = titre
            self.tutorial_body.text = texte
            self._position_tutorial_focus(cible)
        else:
            self.tutorial_focus.enabled = False

    def _position_tutorial_focus(self, cible):
        positions = {
            "jetons": (-0.23, -0.429, 0.64, 0.102),
            "distribuer": (0.53, -0.429, 0.32, 0.078),
            "actions": (0.005, -0.429, 1.08, 0.078),
            "resultat": (0.32, -0.44, 0.73, 0.074),
        }
        if cible not in positions:
            self.tutorial_focus.enabled = False
            return
        x, y, largeur, hauteur = positions[cible]
        haut, bas = y + hauteur / 2, y - hauteur / 2
        gauche, droite = x - largeur / 2, x + largeur / 2
        bord_haut, bord_bas, bord_gauche, bord_droit = self.tutorial_focus_edges
        bord_haut.position = (x, haut, -0.08)
        bord_haut.scale_x = largeur
        bord_bas.position = (x, bas, -0.08)
        bord_bas.scale_x = largeur
        bord_gauche.position = (gauche, y, -0.08)
        bord_gauche.scale_y = hauteur
        bord_droit.position = (droite, y, -0.08)
        bord_droit.scale_y = hauteur
        self.tutorial_focus.enabled = True
