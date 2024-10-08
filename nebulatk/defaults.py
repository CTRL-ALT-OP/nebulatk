try:
    from . import (
        colors_manager,
        fonts_manager,
    )
except ImportError:
    import colors_manager
    import fonts_manager


def _offset(initial, amount):
    if colors_manager.check_full_white_or_black(initial) == -1:
        return initial.brighten(amount)
    else:
        return initial.darken(amount)


class new:
    def __init__(self, file=None):
        if file:
            raise Warning("Not implemented yet")

        self.default_text_color = colors_manager.Color("black")

        self.default_fill = colors_manager.Color("white")

        self.default_border = colors_manager.Color("black")

        self.default_font = fonts_manager.Font("default")
