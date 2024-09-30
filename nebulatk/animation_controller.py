def animate(widget, target_x, target_y):
    while True:
        updated_pos = [target_x, target_y]
        if widget.x != target_x:
            updated_pos[0] = widget.abs_x + ((target_x - widget.x) / 10)
        if widget.y != target_y:
            updated_pos[1] = widget.abs_y + ((target_y - widget.y) / 10)
        if updated_pos == [target_x, target_y]:
            break
        widget.place(updated_pos[0], updated_pos[1])
