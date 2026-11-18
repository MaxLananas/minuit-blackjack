from ursina import AmbientLight, DirectionalLight, Entity, Vec3, color
from ursina.shaders import lit_with_shadows_shader

from objets.ressources import modele


class TableCasino:

    def __init__(self, resources):
        self.resources = resources
        self.root = Entity(name="salon_minuit")
        lit_with_shadows_shader.default_input["shadow_color"] = color.rgba(
            0, 0, 0, 0.25
        )
        self._build_room()
        self._build_table()
        self._build_shoe()
        self.ambient = AmbientLight(color=color.rgb32(220, 205, 190))
        self.sun = DirectionalLight(shadows=False, color=color.rgb32(245, 226, 199))
        self.sun.look_at(Vec3(-1, -2, 1))

    def block(self, position, scale, tint, rotation=(0, 0, 0)):
        return Entity(
            parent=self.root,
            model=modele("bloc"),
            position=position,
            scale=scale,
            rotation=rotation,
            color=color.rgb32(*tint),
        )

    def _build_room(self):
        Entity(
            parent=self.root,
            model=modele("plan"),
            scale=(36, 1, 28),
            y=-2.2,
            texture=self.resources.texture("images/sol.png"),
            texture_scale=(5, 4),
            double_sided=True,
            unlit=True,
        )
        self.block((0, 2.8, 7.2), (30, 11, 0.5), (33, 23, 21))
        self.block((0, -0.4, 6.88), (30, 2.9, 0.15), (56, 35, 27))
        for y, height in ((-1.8, 0.18), (0.95, 0.14), (4.8, 0.16)):
            self.block((0, y, 6.75), (30, height, 0.18), (96, 63, 41))
        for x in range(-12, 13, 3):
            self.block((x, 2.2, 6.73), (0.18, 5.0, 0.16), (66, 44, 32))
            self.block((x + 0.18, 2.2, 6.66), (0.035, 4.8, 0.10), (119, 84, 51))
            self.block((x, -0.4, 6.70), (0.12, 2.35, 0.17), (72, 46, 30))
        self.block((0, 2.55, 6.52), (5.7, 1.74, 0.12), (105, 75, 46))
        self.marquee = Entity(
            parent=self.root,
            model=modele("panneau"),
            position=(0, 2.55, 6.42),
            scale=(5.45, 1.49),
            texture=self.resources.texture("images/enseigne.png"),
            double_sided=True,
            unlit=True,
        )
        for x in (-7.5, -4.25, 4.25, 7.5):
            self.block((x, 2.50, 6.58), (1.10, 2.0, 0.13), (59, 42, 30))
            self.block((x, 2.5, 6.47), (0.92, 1.82, 0.09), (21, 24, 22))
            self.block((x, 2.48, 6.39), (0.03, 1.65, 0.04), (110, 79, 48))
        for x in (-5.9, 5.9):
            self._wall_lamp(x)
        for x in (-8, 8):
            self.block((x, -0.85, 5.8), (2.0, 1.9, 1.0), (48, 34, 27))
            self.block((x, 0.15, 5.77), (2.14, 0.14, 1.08), (105, 65, 41))
            for z in (5.38, 5.83):
                self.block((x, -0.74, z), (1.8, 0.05, 0.05), (91, 62, 41))
        for x in (-4.8, 4.8):
            self.block((x, -1.4, 3.8), (1.15, 0.2, 1.2), (66, 44, 30))
            self.block((x, -0.75, 4.35), (1.2, 1.35, 0.20), (62, 40, 30))
            for dx in (-0.42, 0.42):
                self.block((x + dx, -1.85, 3.8), (0.12, 0.9, 0.12), (64, 43, 30))

    def _wall_lamp(self, x):
        self.block((x, 3.55, 6.42), (0.14, 1.0, 0.12), (128, 92, 52))
        self.block((x, 3.15, 6.18), (0.55, 0.10, 0.62), (140, 96, 49))
        Entity(
            parent=self.root,
            model=modele("boule"),
            position=(x, 3.03, 6.05),
            scale=0.25,
            color=color.rgb32(255, 215, 145),
            unlit=True,
        )

    def _build_table(self):
        Entity(
            parent=self.root,
            model=modele("dessus"),
            texture=self.resources.texture("images/bois.png"),
            color=color.white,
            double_sided=True,
        )
        Entity(
            parent=self.root,
            model=modele("tour"),
            color=color.rgb32(67, 38, 27),
            double_sided=True,
        )
        Entity(
            parent=self.root,
            model=modele("filet"),
            color=color.rgb32(135, 94, 49),
            double_sided=True,
            unlit=True,
        )
        Entity(
            parent=self.root,
            model=modele("rebord"),
            color=color.rgb32(62, 39, 30),
            double_sided=True,
        )
        Entity(
            parent=self.root,
            model=modele("liseret"),
            color=color.rgb32(156, 118, 70),
            double_sided=True,
            unlit=True,
        )
        Entity(
            parent=self.root,
            model=modele("bordure"),
            color=color.rgb32(94, 65, 43),
            double_sided=True,
            unlit=True,
        )
        Entity(
            parent=self.root,
            model=modele("tapis"),
            texture=self.resources.texture("images/tapis.png"),
            color=color.white,
            double_sided=True,
            unlit=True,
        )
        Entity(
            parent=self.root,
            model=modele("plan"),
            position=(0, 0.067, -0.04),
            scale=(10.5, 1, 5.6),
            texture=self.resources.texture("images/inscription.png"),
            double_sided=True,
            unlit=True,
        )
        for x in (-3.9, 3.9):
            self.block((x, -1.35, 0.75), (0.65, 1.4, 0.85), (46, 30, 25))
            self.block((x, -1.96, 0.75), (0.85, 0.14, 1), (92, 62, 39))
        for x in (-5, 5):
            for z in (1.6, 0.8):
                self.block(
                    (x, 0.07, z), (0.10, 0.035, 0.10), (181, 142, 84), (0, 45, 0)
                )

    def _build_shoe(self):
        self.block((4.35, 0.22, 1.75), (1.18, 0.32, 1.65), (49, 36, 31))
        self.block((4.35, 0.40, 1.75), (1.06, 0.06, 1.52), (215, 205, 186))
        Entity(
            parent=self.root,
            model=modele("plan"),
            position=(4.35, 0.435, 1.75),
            scale=(1.04, 1, 1.5),
            texture=self.resources.texture("cartes/dos.png"),
            double_sided=True,
            unlit=True,
        )
        for y in (0.18, 0.27, 0.36):
            self.block((4.35, y, 0.91), (1.07, 0.013, 0.015), (150, 109, 65))
