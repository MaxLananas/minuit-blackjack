from ursina import Button, Entity, Text, color

from ecran.polices import garder_polices
from objets.ressources import modele

garder_polices()

CREAM = color.rgb32(236, 228, 211)
GOLD = color.rgb32(219, 180, 112)
MUTED = color.rgb32(174, 163, 145)
PANEL = color.rgba32(25, 23, 22, 245)
EDGE = color.rgba32(157, 118, 76, 190)
DARK = color.rgb32(28, 24, 22)
BUTTON = color.rgb32(57, 48, 42)
BUTTON_HOVER = color.rgb32(89, 69, 53)
BUTTON_DOWN = color.rgb32(38, 33, 29)
DISABLED = color.rgb32(44, 41, 38)
SANS = "barlow-normal.ttf"
SANS_BOLD = "barlow-gras.ttf"


def panel(parent, position, size, tint=PANEL, depth=0):
    return Entity(
        parent=parent,
        model=modele("panneau"),
        position=(position[0], position[1], depth),
        scale=(size[0], size[1]),
        color=tint,
    )


def etiquette(
    parent,
    text,
    position,
    size=0.8,
    tint=CREAM,
    font=SANS,
    origin=(-0.5, 0.5),
    depth=-0.03,
):
    return Text(
        parent=parent,
        text=text,
        position=(position[0], position[1], depth),
        origin=origin,
        scale=size * 1.22 if size < 0.8 else size,
        color=tint,
        font=font,
        use_tags=False,
    )


def line(parent, position, size, tint=EDGE, depth=-0.01):
    return panel(parent, position, size, tint, depth)


class BoutonCasino(Button):

    def __init__(
        self,
        parent,
        text,
        position,
        size,
        callback,
        *,
        primary=False,
        shape="plaque",
        text_size=0.75,
        base_color=None,
    ):
        normal = base_color if base_color is not None else (GOLD if primary else BUTTON)
        super().__init__(
            parent=parent,
            text=text,
            model=modele("plaque" if shape == "plaque" else "panneau"),
            position=(position[0], position[1], -0.05),
            scale=size,
            color=normal,
            text_color=DARK if primary else CREAM,
            text_size=text_size,
            highlight_scale=1,
            pressed_scale=0.97,
            double_sided=True,
        )
        self._callback = callback
        self.normal_color = normal
        self.normal_text = DARK if primary else CREAM
        self.hover_color = color.rgb32(245, 205, 144) if primary else BUTTON_HOVER
        self.down_color = color.rgb32(180, 133, 74) if primary else BUTTON_DOWN
        if base_color is not None:
            self.hover_color = base_color.tint(0.13)
            self.down_color = base_color.tint(-0.12)
        self.highlight_color = self.hover_color
        self.pressed_color = self.down_color
        self.text_entity.font = SANS_BOLD
        if shape == "plaque":
            Entity(
                parent=self,
                model=modele("panneau"),
                position=(-0.425, 0, -0.01),
                scale=(0.012, 0.50),
                color=color.rgba32(16, 30, 54, 155)
                if primary
                else color.rgba32(157, 118, 76, 180),
            )
        self.on_click = self._activate
        self.available = True

    def _activate(self):
        if self.available and not self.disabled:
            self._callback()

    def set_available(self, available):
        self.available = bool(available)
        self.disabled = not self.available
        self.color = self.normal_color if self.available else DISABLED
        self.text_color = (
            self.normal_text if self.available else color.rgb32(128, 121, 109)
        )
        self.highlight_color = self.hover_color if self.available else DISABLED
        self.pressed_color = self.down_color if self.available else DISABLED
        if self.model:
            self.model.setColorScale(self.color)
