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
        text="Two-axis scroll demo (horizontal + vertical grid scrolling)",
        width=560,
        height=28,
        justify="left",
        fill="#2a4478d0",
        text_color="#ecf2ffff",
        border_width=0,
        font=("Helvetica", 14),
    ).place(24, 332)

    grid_columns = 10
    grid_rows = 16
    cell_width = 140
    cell_height = 56
    grid_gap = 8
    grid_padding = 10
    grid_origin_x = 10
    grid_origin_y = 74

    content_width = (
        (grid_padding * 2)
        + (grid_columns * cell_width)
        + ((grid_columns - 1) * grid_gap)
    )
    content_height = (
        (grid_origin_y + grid_padding)
        + (grid_rows * cell_height)
        + ((grid_rows - 1) * grid_gap)
    )

    content = ntk.Frame(
        viewport,
        width=content_width,
        height=content_height,
        fill="#1a2b4d00",
        border_width=0,
    ).place(6, 6)

    ntk.Frame(
        content,
        width=420,
        height=52,
        fill="#7aa2ffd0",
        border="#e7f0ffff",
        border_width=1,
    ).place(8, 8)
    ntk.Label(
        content,
        text="Drag bottom bar for X, right bar for Y.",
        width=408,
        height=44,
        justify="left",
        fill="#7aa2ffd0",
        border_width=0,
        font=("Helvetica", 13),
    ).place(14, 12)

    for row in range(grid_rows):
        for col in range(grid_columns):
            cell_x = grid_origin_x + col * (cell_width + grid_gap)
            cell_y = grid_origin_y + row * (cell_height + grid_gap)
            row_even = row % 2 == 0
            col_even = col % 2 == 0
            if row_even == col_even:
                cell_fill = "#2a4478aa"
            else:
                cell_fill = "#35548eaa"
            ntk.Frame(
                content,
                width=cell_width,
                height=cell_height,
                fill=cell_fill,
                border="#5f7bb8aa",
                border_width=1,
            ).place(cell_x, cell_y)
            ntk.Label(
                content,
                text=f"r{row + 1:02d} c{col + 1:02d}",
                width=cell_width - 12,
                height=cell_height - 12,
                justify="left",
                fill="#ffffff00",
                text_color="#ecf2ffff",
                border_width=0,
                font=("Helvetica", 13),
            ).place(cell_x + 6, cell_y + 6)

    max_scroll_x = max(0, content_width - viewport.width + 12)
    max_scroll_y = max(0, content_height - viewport.height + 12)

    def apply_scroll(x, y):
        h_track = max(1, h_scrollbar.width - h_scrollbar.button.width)
        h_ratio = float(h_scrollbar.button.x) / float(h_track)
        x_offset = int(round(max_scroll_x * h_ratio))

        v_track = max(1, v_scrollbar.height - v_scrollbar.button.height)
        v_ratio = float(v_scrollbar.button.y) / float(v_track)
        y_offset = int(round(max_scroll_y * v_ratio))

        content.place(6 - x_offset, 6 - y_offset)

    h_scrollbar = ntk.Scrollbar(
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
        direction="horizontal",
        scroll_target=viewport,
        side_scrolling=True,
        dragging_command=apply_scroll,
    ).place(24, 370)

    v_scrollbar = ntk.Scrollbar(
        window,
        width=24,
        height=300,
        fill="#1a2646d8",
        border="#5f7bb8ff",
        border_width=1,
        slider_width=24,
        slider_height=72,
        slider_fill="#7aa2ffd8",
        slider_active_fill="#a5bfffd8",
        slider_hover_fill="#8fb2ffd8",
        slider_active_hover_fill="#c0d2ffd8",
        slider_border="#0b1020ff",
        slider_border_width=1,
        direction="vertical",
        scroll_target=viewport,
        dragging_command=apply_scroll,
    ).place(592, 24)

    apply_scroll(0, 0)


if __name__ == "__main__":
    __main__()
