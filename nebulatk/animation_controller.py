import math


def animate(widget, target_x, target_y):
    position = [widget.x, widget.y]
    while True:
        updated_pos = [target_x, target_y]
        if position[0] != target_x:
            if target_x - position[0] < 0:
                updated_pos[0] = position[0] + min((target_x - position[0]) / 10, -1)
            else:
                updated_pos[0] = position[0] + max((target_x - position[0]) / 10, 1)
        if position[1] != target_y:
            if target_y - position[1] < 0:
                updated_pos[1] = widget.y + min((target_y - position[1]) / 10, -1)
            else:
                updated_pos[1] = widget.y + max((target_y - position[1]) / 10, 1)
        if [math.floor(updated_pos[0]), math.floor(updated_pos[1])] == [
            target_x,
            target_y,
        ]:
            widget.place(target_x, target_y)
            break
        widget.place(updated_pos[0], updated_pos[1])
        position = updated_pos
