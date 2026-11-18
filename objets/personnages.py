from direct.actor.Actor import Actor
from panda3d.core import Filename, LoaderOptions


def load_character(path):
    actor = Actor()
    options = LoaderOptions(actor.modelLoaderOptions)
    options.setFlags(options.getFlags() | LoaderOptions.LFNoCache)
    actor.modelLoaderOptions = options
    actor.loadModel(Filename.fromOsSpecific(str(path.resolve())).getFullpath())
    return actor


class Personnages:

    def __init__(self):
        self.holders = []
        self.actors = []
        self._add("croupier.bam", (0, -2.2, 3.7), 0.92, 0, "Man")
        self._add("marc.bam", (-4.9, -2.2, 3.2), 0.82, -12, "Man")
        self._add("lea.bam", (4.9, -2.2, 3.2), 0.82, 12, "Female")
        print("MINUIT : personnages et couleurs charges.")

    def _add(self, filename, position, scale, angle, kind):
        from ursina import Entity, scene

        from objets.ressources import ASSET_ROOT

        path = ASSET_ROOT / "modeles" / filename
        if not path.is_file():
            raise FileNotFoundError(f"Personnage manquant : {path}")
        holder = Entity(parent=scene, position=position, rotation_y=angle)
        holder.clearShader()
        holder.clearColor()
        actor = load_character(path)
        actor.reparentTo(holder)
        actor.setScale(scale)
        actor.setShaderOff(100)
        actor.setLightOff(100)
        actor.setTextureOff(100)
        actor.setFogOff(100)
        clip = f"HumanArmature|{kind}_Idle"
        if clip not in actor.getAnimNames():
            raise ValueError(f"Animation absente dans {filename} : {clip}")
        actor.loop(clip)
        self.holders.append(holder)
        self.actors.append(actor)
