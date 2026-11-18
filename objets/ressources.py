import builtins
from copy import copy
from functools import lru_cache
from pathlib import Path

from panda3d.core import Filename
from ursina import Texture

ASSET_ROOT = Path(__file__).resolve().parents[1] / "ressources"


@lru_cache(maxsize=32)
def charger_modele(nom):
    chemin = ASSET_ROOT / "modeles" / f"{nom}.bam"
    if not chemin.is_file():
        raise FileNotFoundError(f"Modèle manquant : {chemin}")
    objet = builtins.loader.loadModel(
        Filename.fromOsSpecific(str(chemin)).getFullpath()
    )
    objet.setPos(0, 0, 0)
    return objet


def modele(nom):
    return copy(charger_modele(nom))


class Ressources:

    def __init__(self):
        self._textures = {}

    def texture(self, relative_path):
        path = ASSET_ROOT / relative_path
        if path not in self._textures:
            if not path.is_file():
                raise FileNotFoundError(f"Ressource manquante : {path}")
            self._textures[path] = Texture(path, filtering="bilinear")
        return self._textures[path]

    def face(self, carte):
        return self.texture(f"cartes/{carte.rang}_{carte.couleur.value}.png")
