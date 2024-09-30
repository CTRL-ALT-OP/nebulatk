import nebulatk as ntk
import os
import random
import threading
from time import sleep

fonts = [
    "Cooper Black",
    "Forte",
    "Comic Sans MS Bold",
    "Bauhaus 93",
    "Harlow Solid Italic",
]

colors = [
    "FD3A4A",
    "FD3A4A",
    "A7F432",
    "5DADEC",
    "BFAFB2",
    "FF5470",
    "FFDB00",
    "FF7A00",
    "#45ba52",
    "#2a89d5",
    "#5c21de",
    "#d14d2e",
]

images = [f"Images\\cloud{i}.png" for i in range(1, 5)]

labels = []


# tween
def animate(widget, target_x, target_y):
    while True:
        sleep(0.01)
        updated_pos = [target_x, target_y]
        if widget.x != target_x:
            updated_pos[0] = widget.abs_x + ((target_x - widget.x) / 10)
        if widget.y != target_y:
            updated_pos[1] = widget.abs_y + ((target_y - widget.y) / 10)
        if updated_pos == [target_x, target_y]:
            break
        widget.place(updated_pos[0], updated_pos[1])


def add_text():
    global entry_text
    global display
    global labels
    global canvas2
    global x
    global y
    global last_random
    print(x, y)

    font_size = random.randint(80, 100)

    font = (
        fonts[random.randint(0, len(fonts) - 1)],
        font_size,
    )

    width, height = ntk.fonts_manager.get_min_button_size(
        entry_text.master, font=font, text=entry_text.get()
    )
    if width / height < 820 / 500:
        width = (820 / 500) * height * 1.5
        height = height * 1.5
    else:
        width = width * 1.5
        height = (500 / 820) * width * 1.5
    image = images[random.randint(0, len(images) - 1)]

    iterations = 0
    invalid_location = True
    position = (x, y)
    while invalid_location:
        if last_random:
            position = (random.randint(0, 192) * 10, random.randint(0, 108) * 10)
        label_new = [
            position[0],  # x
            position[1],  # y
            width + position[0],  # x2
            height + position[1],  # y2
        ]
        invalid_location = False
        if label_new[2] > 1920 or label_new[3] > 1080:
            invalid_location = True
        else:
            for label in labels:
                if (
                    label_new[2] >= label[0]
                    and label_new[0] <= label[2]
                    and label_new[1] <= label[3]
                    and label_new[3] >= label[1]
                ):
                    invalid_location = True
                    break
        iterations += 1
        if iterations >= 100:
            font_size -= 5
            font = (
                font[0],
                font_size,
            )
            width, height = ntk.fonts_manager.get_min_button_size(
                entry_text.master, font=font, text=entry_text.get()
            )
            if width / height < 820 / 500:
                width = (820 / 500) * height * 1.5
                height = height * 1.5
            else:
                width = width * 1.5
                height = (500 / 820) * width * 1.5
            iterations = 0
    color = colors[random.randint(0, len(colors) - 1)]
    angle = random.randint(-30, 30)
    lbl = ntk.Label(
        display,
        text=entry_text.get(),
        height=height,
        width=width,
        image=(image, 150, angle, (255, 255, 255)),
        font=font,
        text_color=color,
        angle=angle,
    )
    lbl.place(random.randint(0, 1920), 1920 + lbl.height)
    ntk.Label(
        canvas2,
        text=entry_text.get(),
        height=height / 5,
        width=width / 5,
        # image=(image, 50, (255, 255, 255)),
        font=(font[0], int(font[1] / 5)),
        text_color=color,
    ).place(position[0] / 5, position[1] / 5)
    labels.append(label_new)
    threading.Thread(target=animate, args=(lbl, position[0], position[1])).start()

    x = random.randint(0, 192) * 10
    y = random.randint(0, 108) * 10
    last_random = True


# NOTE: EXAMPLE WINDOW
def __main__():
    for file in os.listdir("Fonts"):
        print(file)
        ntk.fonts_manager.loadfont(file, private = False)
    global x
    global y
    global last_random
    last_random = True
    x = random.randint(0, 192) * 10
    y = random.randint(0, 108) * 10

    global display
    display = ntk.Window(1920, 1080, resizable=False, override=True).place(1920)
    entry = ntk.Window(384, 50 + 216, resizable=False, closing_command=display.close)

    global entry_text
    entry_text = ntk.Entry(
        entry,
        text="",
        font=("Helvetica", 20),
        width=300,
        height=50,
        justify="left",
        fill=[0, 100, 0, 50],
        border_width=1,
        text_color="cobaltgreen",
    ).place(0, 0)

    ntk.Button(
        entry,
        text="Enter",
        width=50,
        height=50,
        fill=[0, 100, 0, 50],
        command=add_text,
    ).place(300, 0)

    def clicked(event):
        global x
        global y
        global last_random
        if event.y > 50:
            last_random = False
            x, y = event.x * 5, (event.y - 50) * 5

    entry.bind("<Button-1>", clicked)

    ntk.Frame(
        display, width=1920, height=1080, image="Images/background2.jpg"
    ).place()

    global canvas2
    canvas2 = ntk.Frame(
        entry, width=384, height=216, image="Images/background2.jpg"
    ).place(0, 50)


if __name__ == "__main__":
    __main__()