from _example_utils import use_local_nebulatk

use_local_nebulatk()

import nebulatk as ntk


def __main__():
    window = ntk.Window(
        width=760,
        height=420,
        title="Container Scroll Demo",
        render_mode="image_gl",
        fps=60,
        background_color="#111a30ff",
    )

    # Full-window overlay in the main window to prove top-level alpha compositing.
    ntk.Frame(
        window,
        width=760,
        height=420,
        fill="#b04dd044",
        border_width=0,
    ).place(0, 0)
    ntk.Label(
        window,
        text="Main window overlay (semi-transparent)",
        width=350,
        height=30,
        justify="left",
        fill="#4dd0e166",
        text_color="#ffffffff",
        border_width=0,
        font=("Helvetica", 12),
    ).place(390, 12)

    # High-contrast backdrop to prove alpha blending through container layers.
    for idx in range(10):
        stripe_fill = "#263d6aff" if idx % 2 == 0 else "#1a2e52ff"
        ntk.Frame(
            window,
            width=760,
            height=30,
            fill=stripe_fill,
            border_width=0,
        ).place(0, (idx * 30))

    viewport = ntk.Container(
        window,
        width=560,
        height=300,
        fill="#20345f00",
        border="#b8cdffff",
        border_width=3,
    ).place(24, 24)

    ntk.Label(
        window,
        text="Scrollable container demo (clipped + transparency through container)",
        width=560,
        height=28,
        justify="left",
        fill="#2a4478d0",
        text_color="#ecf2ffff",
        border_width=0,
        font=("Helvetica", 14),
    ).place(24, 332)

    content_height = 920
    content = ntk.Frame(
        viewport,
        width=548,
        height=content_height,
        fill="#1a2b4d00",
        border_width=0,
    ).place(6, 6)

    ntk.Frame(
        content,
        width=532,
        height=52,
        fill="#7aa2ffd0",
        border="#e7f0ffff",
        border_width=1,
    ).place(8, 8)
    ntk.Label(
        content,
        text="Top marker: stripes behind this panel should remain visible.",
        width=520,
        height=44,
        justify="left",
        fill="#7aa2ffd0",
        border_width=0,
        font=("Helvetica", 13),
    ).place(14, 12)

    for idx in range(22):
        row_y = 72 + (idx * 40)
        row_fill = "#2a4478aa" if idx % 2 == 0 else "#35548eaa"
        ntk.Frame(
            content,
            width=532,
            height=34,
            fill=row_fill,
            border="#5f7bb8aa",
            border_width=1,
        ).place(8, row_y)
        ntk.Label(
            content,
            text=f"Row {idx + 1:02d}  -  Scroll offset driven by slider",
            width=520,
            height=30,
            justify="left",
            fill="#ffffff00",
            text_color="#ecf2ffff",
            border_width=0,
            font=("Helvetica", 13),
        ).place(14, row_y + 2)

    scrollbar = ntk.Slider(
        window,
        width=560,
        height=24,
        fill="#1a2646d8",
        border="#5f7bb8ff",
        border_width=1,
        slider_width=84,
        slider_height=24,
        slider_fill="#7aa2ffd8",
        slider_active_fill="#a5bfffd8",
        slider_hover_fill="#8fb2ffd8",
        slider_active_hover_fill="#c0d2ffd8",
        slider_border="#0b1020ff",
        slider_border_width=1,
    ).place(24, 370)

    max_scroll = max(0, content_height - viewport.height + 12)
    _last_offset = {"value": None}

    def sync_scroll():
        track_width = max(1, scrollbar.width - scrollbar.button.width)
        ratio = float(scrollbar.button.x) / float(track_width)
        offset = int(round(max_scroll * ratio))
        if offset != _last_offset["value"]:
            content.place(6, 6 - offset)
            _last_offset["value"] = offset
        window.root.after(16, sync_scroll)

    sync_scroll()


if __name__ == "__main__":
    __main__()
