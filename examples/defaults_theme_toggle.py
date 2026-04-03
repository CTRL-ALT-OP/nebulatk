from _example_utils import use_local_nebulatk, example_path

use_local_nebulatk()

import nebulatk as ntk


def __main__():
    light_defaults = example_path("defaults_light.py")
    dark_defaults = example_path("defaults_dark.py")

    window = ntk.Window(
        width=620,
        height=360,
        title="Defaults + Styles Demo",
        defaults_file=light_defaults,
    )

    state = {"dark": False}

    header = ntk.Label(
        window,
        style=window.defaults.label_header,
        text="Dynamic Defaults + Style Inheritance",
    ).place(40, 20)

    primary = ntk.Button(
        window,
        style=window.defaults.button_1,
        text="Primary Style (button_1)",
    ).place(40, 100)

    secondary = ntk.Button(
        window,
        style=window.defaults.button_2,
        text="Secondary Style (button_2 extends button_1)",
    ).place(40, 160)

    overridden = ntk.Button(
        window,
        style=window.defaults.button_1,
        text="Explicit override fill (#aa4b00)",
        fill="#aa4b00",
    ).place(40, 220)

    def toggle_theme():
        state["dark"] = not state["dark"]
        target = dark_defaults if state["dark"] else light_defaults
        window.set_defaults(target)
        toggle_btn.text = "Switch to light" if state["dark"] else "Switch to dark"
        header.text = (
            "Dark defaults loaded"
            if state["dark"]
            else "Light defaults loaded"
        )

    toggle_btn = ntk.Button(
        window,
        width=180,
        height=40,
        text="Switch to dark",
        command=toggle_theme,
    ).place(400, 280)

    # Keep references alive and visible in the example.
    _ = (primary, secondary, overridden)


if __name__ == "__main__":
    __main__()
