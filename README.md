# NebulaTk

NebulaTk is an early-stage, Tkinter-style GUI toolkit with a custom widget/rendering
pipeline. Widgets are composed into Pillow images and displayed through an OpenGL
window backend.

Questions, bug reports, and feature requests: `ctrl.alt.op@gmail.com` or through this GitHub repo

## Current status

- Project is in active early development.
- The current `Window()` path in this branch supports `render_mode="image_gl"` only, but might be expanded for vulkan later.
- Rendering currently depends on a GLFW + PyOpenGL backend.

## Installation

From the repository root:

```bash
pip install -e .
```

For development and tests:

```bash
pip install -r requirements.txt
```

## Quick start

```python
import nebulatk as ntk

window = ntk.Window(title="NebulaTk")
ntk.Button(window, text="Hello NebulaTk").place(20, 20)
```

You can also run included examples:

```bash
python examples/example.py
python examples/relativeplace.py
python examples/word_collage.py
python examples/defaults_theme_toggle.py
```

Note: example scripts may reference local assets under `examples/Images/`. If those
assets are missing in your checkout, update image paths or provide your own files.

## Defaults, themes, and styles

NebulaTk supports file-backed defaults through `nebulatk/defaults.py`. This lets you:

- Define app-wide default colors/fonts in a Python module.
- Define named reusable styles (for example `button_1`, `button_2`).
- Inherit styles from other styles with `extends`.
- Switch defaults at runtime and update all widgets that are still default-bound.

### 1) Create a defaults file

Create a Python file (for example `my_defaults_light.py`):

```python
DEFAULTS = {
    "default_text_color": "#101010",
    "default_fill": "#ffffff",
    "default_border": "#222222",
    # -1 means "auto size", dynamically recomputed for default-bound widgets
    "default_font": ("Helvetica", -1, "normal"),
    # Used by Window(background_color="default") and by default Window()
    "default_window_background": "#f4f7ff",
}

STYLES = {
    "button_1": {
        "fill": "#d7e8ff",
        "text_color": "#112244",
        "border": "#4477aa",
        "border_width": 2,
    },
    "button_2": {
        "extends": "button_1",
        "fill": "#e9f6d2",
    },
}
```

You can also use:

- `PROFILE = {"defaults": {...}, "styles": {...}}` in one object, or
- lowercase `defaults`/`styles`.

### 2) Load defaults when creating a window

```python
import nebulatk as ntk

window = ntk.Window(
    title="Themed App",
    defaults_file="my_defaults_light.py",
)
```

### 3) Use default-bound widget values

Properties set to `"default"` (or `font=None`/`font="default"`) are owned by the
defaults system and update when defaults change.

```python
btn = ntk.Button(
    window,
    text="Save",
    fill="default",
    border="default",
    text_color="default",
    font="default",
).place(20, 20)
```

For image-backed widgets, default `fill` and default `border` are transparent by
design so image edges are not covered.

### 4) Apply named styles

Use style references from `window.defaults`:

```python
primary = ntk.Button(
    window,
    text="Primary",
    style=window.defaults.button_1,
    width=160,
    height=44,
).place(20, 80)

secondary = ntk.Button(
    window,
    text="Secondary",
    style=window.defaults.button_2,
    width=160,
    height=44,
).place(20, 140)
```

You may also pass a style name string directly:

```python
ntk.Button(window, text="Inline Name", style="button_1").place(200, 80)
```

### 5) Override style/default values per widget

If you set a concrete value, that property is no longer default-bound for that
widget and will not be changed by later theme switches.

```python
danger = ntk.Button(
    window,
    text="Delete",
    style=window.defaults.button_1,
    fill="#aa0000",  # explicit override
).place(20, 200)
```

In this example, `danger.fill` remains `#aa0000` after defaults are switched, while
other style/default-bound fields still update.

### 6) Switch themes at runtime

Use `window.set_defaults(...)` to load a different defaults file:

```python
is_dark = False

def toggle_theme():
    global is_dark
    is_dark = not is_dark
    target = "my_defaults_dark.py" if is_dark else "my_defaults_light.py"
    window.set_defaults(target)

ntk.Button(window, text="Toggle Theme", command=toggle_theme).place(20, 260)
```

When switched, all widgets that still use default-bound values (including style-bound
fields) are updated automatically across the app.

### 7) Dynamic default font sizing behavior

If a widget is using the default font with size `-1`, NebulaTk recomputes the font
size when widget size/text constraints change (for example resize/reflow). Once you set
an explicit font size (for example `("Helvetica", 13, "normal")`), that widget stops
auto-resizing its font and keeps the explicit size.

## Running tests

From the project root:

```bash
pytest
```

## Public API highlights

Top-level imports exposed by `nebulatk` include:

- `Window`
- `FileDialog`
- Widgets: `Button`, `Label`, `Entry`, `Frame`, `Slider`, `Container`
- Utility modules: `colors_manager`, `fonts_manager`, `image_manager`,
  `bounds_manager`, `standard_methods`, `animation_controller`, `rendering`,
  `file_manager`

Many widget methods are chainable, for example:

```python
ntk.Button(window, text="Chainable").place(10, 10).hide().show()
```

## Project layout

- `nebulatk/` - main package source
- `nebulatk/widgets/` - widget classes and base components
- `examples/` - runnable usage demos
- `tests/` - `pytest` test suite

## Notes

- This project is not a drop-in implementation of Tk's internal event/render loop.
- The window/rendering architecture uses both threading and multiprocessing internally.