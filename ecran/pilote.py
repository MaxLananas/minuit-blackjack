import math
import time

from ursina import Entity, Vec3, application, camera, color

from ecran.boutons import panel
from ecran.menus import InterfaceJeu
from ecran.rythme import EtapeAnimation, SuiteAnimations
from ecran.sons import BanqueSons
from jeu.cartes import PaquetEpuise
from jeu.manche import ActionImpossible, Etat, SoldeInsuffisant
from jeu.salon import SalonBlackjack
from objets.ressources import Ressources
from objets.scene import SceneTable

SOLDE_INITIAL_MAX = 1_000_000


def ease(progress):
    return progress * progress * (3 - 2 * progress)


class ControleurJeu(Entity):

    def __init__(self, solde_initial=1000, fabrique_paquet=None):
        super().__init__(name="controleur")
        self.solde_initial = solde_initial
        self.partie = SalonBlackjack(solde_initial, fabrique_paquet=fabrique_paquet)
        self.difficulte = "normal"
        self.tutorial_active = False
        self.resources = Ressources()
        self.sound = BanqueSons()
        self.table = SceneTable(self.resources)
        self.timeline = SuiteAnimations(self.refresh, self._animation_error)
        self.ui = InterfaceJeu(self)
        self.screen = "menu"
        self.modal = None
        self.settings_origin = None
        self.paused = False
        self.has_session = False
        self.notice = ""
        self.notice_time = 0.0
        self.camera_focus = -1.35
        self.camera_focus_goal = -1.35
        self.intro_time = 0.0
        self.fade_time = 1.15
        self.fade = panel(
            camera.ui, (0, 0), (2, 1.1), color.rgba32(12, 10, 9, 255), depth=-1
        )
        camera.position = (0, 8.5, -16.5)
        camera.look_at(Vec3(self.camera_focus, 0.6, 0))
        camera.fov = 45
        self.ui.show_menu(False)
        self.refresh()

    def update(self):
        delta = min(time.dt, 0.1)
        self.intro_time += delta
        intro = ease(min(1.0, self.intro_time / 1.25))
        camera.position = Vec3(0, 8.5 - intro * 0.5, -16.5 + 0.8 * intro)
        self.camera_focus += (self.camera_focus_goal - self.camera_focus) * min(
            1, delta * 3.8
        )
        camera.look_at(Vec3(self.camera_focus, 0.6, 0))
        if self.fade_time > 0:
            self.fade_time = max(0.0, self.fade_time - delta)
            self.fade.color = color.rgba(
                0.035, 0.028, 0.023, min(1, self.fade_time / 0.75)
            )
            self.fade.enabled = self.fade_time > 0
        if self.notice_time > 0:
            self.notice_time -= delta
            if self.notice_time <= 0:
                self.notice = ""
                self.refresh()
        if not self.paused and self.screen == "game":
            self.timeline.update(delta)

    def input(self, key):
        if self.screen == "menu" and self.modal is None:
            if key in ("up arrow", "w"):
                self.ui.select_menu(self.ui.menu_index - 1)
                self.sound.play("click")
                return
            if key in ("down arrow", "s"):
                self.ui.select_menu(self.ui.menu_index + 1)
                self.sound.play("click")
                return
            if key in ("enter", "space"):
                self.ui.activate_menu()
                return
        if key != "escape":
            return
        if self.modal == "settings":
            self.close_settings()
        elif self.modal == "history":
            self.close_history()
        elif self.modal == "confirm":
            self.cancel_reset()
        elif self.screen == "game":
            self.toggle_pause()

    def refresh(self):
        self.ui.refresh(self.partie, busy=self.timeline.busy, notice=self.notice)

    def _message(self, message):
        self.notice = str(message)
        self.notice_time = 3.5
        self.refresh()

    def _clear_message(self):
        self.notice = ""
        self.notice_time = 0.0

    def _animation_error(self, error):
        self._message(
            "Une animation a échoué. Utilisez Pause pour recommencer la session."
        )

    def _can_play(self):
        return (
            self.screen == "game"
            and self.modal is None
            and not self.paused
            and not self.timeline.busy
        )

    def _transition(self):
        self.fade_time = 0.38
        self.fade.enabled = True
        self.fade.color = color.rgba(0.035, 0.028, 0.023, 0.45)

    def enter_game(self):
        if self.screen != "menu" or self.modal is not None:
            return
        self.sound.play("click")
        if not self.has_session:
            self.partie.reinitialiser_session(self.solde_initial)
            self.table.clear_cards()
            self.table.sync(self.partie)
            self.has_session = True
        self.screen = "game"
        self.modal = None
        self.paused = False
        self.camera_focus_goal = 0
        self.table.table.marquee.color = color.white
        self.ui.show_game()
        self._transition()
        self.refresh()

    def return_to_menu(self):
        if self.screen != "game" or self.modal != "pause":
            return
        self.sound.play("click")
        self.screen = "menu"
        self.modal = None
        self.paused = True
        self.camera_focus_goal = -1.35
        self.table.table.marquee.color = color.white
        self.ui.show_menu(True)
        self._transition()

    def add_chip(self, valeur):
        if not self._can_play():
            return
        try:
            self.partie.miser(valeur)
        except (ActionImpossible, ValueError) as error:
            self._message(error)
            return
        self.sound.play("chip")
        self._clear_message()
        self.table.sync(self.partie)
        self.refresh()

    def effacer_mise(self):
        if not self._can_play():
            return
        try:
            self.partie.effacer_mise()
        except ActionImpossible as error:
            self._message(error)
            return
        self.sound.play("chip")
        self._clear_message()
        self.table.sync(self.partie)
        self.refresh()

    def deal(self):
        if not self._can_play():
            return
        try:
            self.partie.commencer_manche()
        except (ActionImpossible, PaquetEpuise) as error:
            self._message(error)
            return
        self._clear_message()
        self.table.clear_cards()
        self.timeline.start(self._initial_deal())
        self.refresh()

    def _movement(self, movements, duration=0.36):
        def move(progress):
            montant = ease(progress)
            for entity, start, cible in movements:
                entity.position = start + (cible - start) * montant
                if start.y - cible.y > 0.1:
                    entity.y += math.sin(progress * math.pi) * 0.18

        return EtapeAnimation(duration, move)

    def _initial_deal(self):
        for _ in range(self.partie.nombre_cartes_depart):
            self.partie.distribuer_carte()
            self.sound.play("card")
            movements = self.table.sync(self.partie, animate_new=True)
            self.refresh()
            yield self._movement(movements)
            yield EtapeAnimation(0.06)
        yield from self._continue_round()

    def player_action(self, name):
        if not self._can_play():
            return
        if name not in self.partie.actions_autorisees():
            self._message("Cette action n'est pas disponible.")
            return
        self._clear_message()
        self.timeline.start(self._play_action(name))
        self.refresh()

    def _action_sound(self, name):
        if name == "separer":
            self.sound.play("chip")
        elif name == "rester":
            self.sound.play("click")
        else:
            self.sound.play("card")

    def _play_action(self, name):
        actions = {
            "tirer": self.partie.tirer,
            "rester": self.partie.rester,
            "doubler": self.partie.doubler,
            "separer": self.partie.separer,
        }
        actions[name]()
        self._action_sound(name)
        movements = self.table.sync(self.partie, animate_new=name != "rester")
        self.refresh()
        if name != "rester":
            yield self._movement(movements, 0.44 if name == "separer" else 0.36)
        else:
            yield EtapeAnimation(0.12)
        yield from self._continue_round()

    def _continue_round(self):
        while self.partie.etat == Etat.TOUR_RIVAUX:
            self.refresh()
            yield EtapeAnimation(0.30)
            choice = self.partie.choisir_action_rival(self.difficulte)
            self.partie.faire_jouer_rival(choice)
            self._action_sound(choice)
            movements = self.table.sync(self.partie, animate_new=choice != "rester")
            self.refresh()
            if choice != "rester":
                yield self._movement(movements, 0.40 if choice == "separer" else 0.32)
            else:
                yield EtapeAnimation(0.18)
        if self.partie.etat == Etat.TOUR_CROUPIER:
            self.partie.reveler_croupier()
            view = self.table.prepare_reveal(self.partie)
            if view:
                self.sound.play("card")
                yield EtapeAnimation(
                    0.48,
                    lambda progress: setattr(
                        view.pivot, "rotation_z", 180 * (1 - ease(progress))
                    ),
                )
            self.refresh()
            yield EtapeAnimation(0.2)
            while self.partie.etat == Etat.TOUR_CROUPIER:
                deal = self.partie.jouer_croupier()
                if deal is None:
                    self.table.sync(self.partie)
                    break
                self.sound.play("card")
                movements = self.table.sync(self.partie, animate_new=True)
                self.refresh()
                yield self._movement(movements)
                yield EtapeAnimation(0.17)
        if self.partie.etat == Etat.REGLEMENT:
            yield EtapeAnimation(0.3)
            bilan = self.partie.regler_manche()
            if bilan.net > 0:
                self.sound.play("win")
            elif bilan.net < 0:
                self.sound.play("lose")
            else:
                self.sound.play("click")
            self.refresh()
        elif (
            self.partie.etat == Etat.MANCHE_TERMINEE
            and self.partie.historique[-1].annulee
        ):
            self.sound.play("lose")
            self.refresh()

    def nouvelle_manche(self):
        if not self._can_play():
            return
        try:
            self.partie.nouvelle_manche()
        except ActionImpossible as error:
            self._message(error)
            return
        self.sound.play("click")
        self._clear_message()
        self.table.clear_cards()
        self.table.sync(self.partie)
        self.refresh()
        if self.partie.solde < 1:
            self._message("Solde trop faible : recommencez une session depuis Pause.")

    def replay(self):
        if not self._can_play():
            return
        try:
            self.partie.nouvelle_manche(repeter_mise=True)
        except (SoldeInsuffisant, ActionImpossible) as error:
            self._message(error)
            return
        self.table.clear_cards()
        self.table.sync(self.partie)
        self.refresh()
        self.deal()

    def toggle_pause(self):
        if self.screen != "game" or self.modal not in (None, "pause"):
            return
        self.sound.play("click")
        self.paused = not self.paused
        self.modal = "pause" if self.paused else None
        self.ui.pause.enabled = self.paused
        self.refresh()

    def open_settings(self):
        if self.modal not in (None, "pause"):
            return
        if self.screen == "game" and self.modal != "pause":
            return
        self.sound.play("click")
        self.settings_origin = self.modal or "menu"
        self.modal = "settings"
        self.ui.pause.enabled = False
        self.ui.settings.enabled = True
        self.ui.balance_feedback.text = "De 1 à 1 000 000 jetons."
        self.ui.balance_feedback.color = color.rgb32(174, 163, 145)
        self.ui.refresh_settings()

    def close_settings(self):
        if self.modal != "settings":
            return
        self.sound.play("click")
        self.ui.balance_input.active = False
        self.ui.settings.enabled = False
        self.modal = None if self.settings_origin == "menu" else "pause"
        self.ui.pause.enabled = self.modal == "pause"

    def select_initial_balance(self, valeur):
        if self.modal != "settings" or valeur not in (500, 1000, 2500):
            return
        self.sound.play("click")
        self.solde_initial = valeur
        self.ui.balance_input.text = str(valeur)
        self.ui.refresh_settings()
        self.ui.balance_feedback.text = "C'est noté pour ta prochaine session."
        self.ui.balance_feedback.color = color.rgb32(219, 180, 112)

    def apply_custom_balance(self):
        if self.modal != "settings":
            return
        self.ui.balance_input.active = False
        try:
            valeur = int(self.ui.balance_input.text.strip())
        except ValueError:
            valeur = 0
        if valeur < 1 or valeur > SOLDE_INITIAL_MAX:
            self.ui.balance_feedback.text = "Choisis entre 1 et 1 000 000 jetons."
            self.ui.balance_feedback.color = color.rgb32(225, 125, 105)
            return
        self.solde_initial = valeur
        self.sound.play("click")
        self.ui.refresh_settings()
        self.ui.balance_feedback.text = "C'est noté pour ta prochaine session."
        self.ui.balance_feedback.color = color.rgb32(219, 180, 112)

    def select_difficulty(self, valeur):
        if self.modal != "settings" or valeur not in ("facile", "normal", "expert"):
            return
        self.sound.play("click")
        self.difficulte = valeur
        self.ui.refresh_settings()

    def start_tutorial(self):
        if self.screen != "menu" or self.modal is not None:
            return
        self.tutorial_active = True
        self.enter_game()
        self.refresh()

    def tutorial_from_pause(self):
        if self.screen != "game" or self.modal != "pause":
            return
        self.tutorial_active = True
        self.toggle_pause()
        self.refresh()

    def end_tutorial(self):
        if not self.tutorial_active or self.modal is not None or self.screen != "game":
            return
        self.tutorial_active = False
        self.sound.play("click")
        self.refresh()

    def toggle_sound(self):
        if self.modal != "settings":
            return
        self.sound.toggle()
        self.sound.play("click")
        self.ui.refresh_settings()

    def open_history(self):
        if self.screen != "game" or self.modal is not None:
            return
        self.sound.play("click")
        self.paused = True
        self.modal = "history"
        self.ui.refresh_history(self.partie)
        self.ui.historique.enabled = True

    def close_history(self):
        if self.modal != "history":
            return
        self.sound.play("click")
        self.ui.historique.enabled = False
        self.modal = None
        self.paused = False
        self.refresh()

    def ask_reset(self):
        if self.modal != "pause":
            return
        self.sound.play("click")
        self.modal = "confirm"
        self.ui.pause.enabled = False
        self.ui.confirm.enabled = True

    def cancel_reset(self):
        if self.modal != "confirm":
            return
        self.sound.play("click")
        self.ui.confirm.enabled = False
        self.ui.pause.enabled = True
        self.modal = "pause"

    def reinitialiser_session(self):
        if self.modal != "confirm":
            return
        self.sound.play("click")
        self.timeline.cancel()
        self.partie.reinitialiser_session(self.solde_initial)
        self.table.clear_cards()
        self.table.sync(self.partie)
        self.ui.confirm.enabled = False
        self.modal = None
        self.paused = False
        self._clear_message()
        self._transition()
        self.refresh()

    def quit_game(self):
        if self.modal not in (None, "pause"):
            return
        application.quit()
