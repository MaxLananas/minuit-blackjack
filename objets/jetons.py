from ursina import Entity, destroy

from objets.ressources import modele

DENOMINATIONS = (500, 100, 25, 5, 1)


class PilesJetons:

    def __init__(self, resources):
        self.resources = resources
        self.root = Entity(name="mises_3d")
        self.meshes = {valeur: modele(f"jeton_{valeur}") for valeur in DENOMINATIONS}
        self.signature = None

    def clear(self):
        for child in tuple(self.root.children):
            destroy(child)
        self.signature = None

    def display(self, amounts):
        signature = tuple(
            (int(montant), round(x, 2), round(z, 2)) for montant, x, z in amounts
        )
        if signature == self.signature:
            return
        self.clear()
        self.signature = signature
        for montant, center_x, center_z in signature:
            groups = []
            remainder = montant
            for valeur in DENOMINATIONS:
                count, remainder = divmod(remainder, valeur)
                if count:
                    while count:
                        part = min(count, 12)
                        groups.append((valeur, part))
                        count -= part
            spacing = 0.47
            total_width = spacing * max(0, len(groups) - 1)
            for index, (valeur, count) in enumerate(groups):
                x = center_x - total_width / 2 + index * spacing
                for level in range(count):
                    y = 0.10 + level * 0.065
                    chip = Entity(
                        parent=self.root,
                        position=(x, y, center_z),
                        scale=(0.41, 0.065, 0.41),
                        double_sided=True,
                    )
                    self.meshes[valeur].copy_to(chip)
                    Entity(
                        parent=self.root,
                        model=modele("plan"),
                        position=(x, y + 0.034, center_z),
                        scale=(0.415, 1, 0.415),
                        texture=self.resources.texture(f"images/jeton_{valeur}.png"),
                        double_sided=True,
                        unlit=True,
                    )
