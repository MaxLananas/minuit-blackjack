from pathlib import Path

from panda3d.core import Filename, loadPrcFileData
from screeninfo import ScreenInfoError, get_monitors
from ursina import Ursina, application, color, window

from ecran.pilote import ControleurJeu


def window_size():
    try:
        monitors = get_monitors()
        monitor = next((item for item in monitors if item.is_primary), monitors[0])
        width = min(1440, monitor.width - 40, int((monitor.height - 52) * 16 / 9))
        width = max(320, width)
        return width, round(width * 9 / 16)
    except (IndexError, OSError, ValueError, ScreenInfoError):
        return 1280, 720


def main():
    loadPrcFileData(
        "", "win-fixed-size true\nframebuffer-multisample 1\nmultisamples 2"
    )
    app = Ursina(
        title="Minuit — Blackjack 21",
        icon=Filename.fromOsSpecific(
            str(
                Path(__file__).resolve().parent / "ressources" / "images" / "minuit.ico"
            )
        ).getFullpath(),
        size=window_size(),
        fullscreen=False,
        borderless=False,
        development_mode=False,
        show_ursina_splash=False,
        editor_ui_enabled=False,
    )
    application.asset_folder = Path(__file__).resolve().parent / "ressources"
    window.color = color.rgb32(20, 17, 15)
    window.fps_counter.enabled = False
    window.exit_button.enabled = False
    window.cog_button.enabled = False
    window.input_entity.enabled = False
    controller = ControleurJeu()
    app.run()
    return controller


if __name__ == "__main__":
    main()
