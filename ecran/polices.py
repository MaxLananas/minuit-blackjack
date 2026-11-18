from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path

from panda3d.core import Filename, FontPool, getModelPath

DOSSIER = Path(__file__).resolve().parents[1] / "ressources" / "polices"


@lru_cache(maxsize=16)
def police(nom):
    paquet = find_spec("ursina")
    interne = (
        Path(paquet.origin).parent / "fonts" if paquet and paquet.origin else DOSSIER
    )
    for dossier in (DOSSIER, interne):
        chemin = dossier / nom
        if chemin.is_file():
            getModelPath().appendPath(Filename.fromOsSpecific(str(dossier.resolve())))
            resultat = FontPool.loadFont(chemin.name)
            if resultat:
                return resultat
    raise FileNotFoundError(f"Police introuvable : {nom}")


def changer_police(texte, nom):
    texte._font = police(nom)
    texte._font.setLineHeight(texte.line_height)
    if texte.text:
        texte.text = texte.raw_text


def regler_resolution(texte, valeur):
    if texte.font is None:
        return
    if texte._font.getPixelsPerUnit() != valeur:
        texte._font.clear()
        texte._font.setPixelsPerUnit(valeur)


def garder_polices():
    from ursina import Text

    Text.font = property(Text.font_getter, changer_police)
    Text.resolution = property(Text.resolution_getter, regler_resolution)
