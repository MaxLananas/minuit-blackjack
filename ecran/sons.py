from ursina import Audio

from objets.ressources import ASSET_ROOT

FICHIERS = {
    "card": (("carte-glisse-1.ogg", "carte-glisse-2.ogg", "carte-pose.ogg"), 0.23),
    "chip": (("jeton-pose-1.ogg", "jeton-pose-2.ogg"), 0.20),
    "click": (("clic.wav",), 0.11),
    "win": (("jetons-pile.ogg",), 0.20),
    "lose": (("carte-pose.ogg",), 0.15),
}


class BanqueSons:

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.indices = {}
        for name, (files, volume) in FICHIERS.items():
            self.sounds[name] = []
            for filename in files:
                path = ASSET_ROOT / "sons" / filename
                if not path.is_file():
                    raise FileNotFoundError(f"Son manquant : {path}")
                self.sounds[name].append(Audio(path, autoplay=False, volume=volume))
            self.indices[name] = 0

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            for variants in self.sounds.values():
                for sound in variants:
                    sound.stop(destroy=False)

    def play(self, name):
        if self.enabled and name in self.sounds:
            variants = self.sounds[name]
            index = self.indices[name] % len(variants)
            self.indices[name] += 1
            variants[index].play()
