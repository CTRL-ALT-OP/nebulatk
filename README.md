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
```

Note: example scripts may reference local assets under `examples/Images/`. If those
assets are missing in your checkout, update image paths or provide your own files.

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