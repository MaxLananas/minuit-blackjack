from ursina import Entity, color, destroy
from ursina.shaders import lit_with_shadows_shader

from objets.ressources import modele


class Carte3D:

    def __init__(self, resources, carte=None, cachee=False, position=(0, 0.16, 0)):
        self.resources = resources
        self.root = Entity(name="carte", position=position)
        self.pivot = Entity(parent=self.root, rotation_z=180 if cachee else 0)
        self.shadow = Entity(
            parent=self.root,
            model=modele("plan"),
            position=(0.06, -0.065, -0.08),
            scale=(1.55, 1, 2.05),
            texture=resources.texture("images/ombre.png"),
            color=color.rgba32(255, 255, 255, 170),
            double_sided=True,
            unlit=True,
        )
        Entity(
            parent=self.pivot,
            model=modele("bloc"),
            scale=(1.15, 0.065, 1.64),
            color=color.rgb32(227, 218, 193),
            shader=lit_with_shadows_shader,
        )
        self.front = Entity(
            parent=self.pivot,
            model=modele("plan"),
            y=0.036,
            scale=(1.15, 1, 1.64),
            texture=resources.face(carte) if carte else None,
            color=color.rgb32(249, 246, 232),
            double_sided=True,
            unlit=True,
        )
        self.back = Entity(
            parent=self.pivot,
            model=modele("plan"),
            y=-0.036,
            rotation=(180, 180, 0),
            scale=(1.15, 1, 1.64),
            texture=resources.texture("cartes/dos.png"),
            color=color.white,
            double_sided=True,
            unlit=True,
        )
        self.carte = carte
        self.cachee = cachee

    def reveal(self, carte):
        self.carte = carte
        self.front.texture = self.resources.face(carte)
        self.cachee = False

    def destroy(self):
        destroy(self.root)
