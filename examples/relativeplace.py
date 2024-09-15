import nebulatk as ntk
from time import sleep


def __main__():
    window = ntk.Window()

    frame = ntk.Frame(window, width=100, height=100, border_width=4).place(50, 25)

    btn = ntk.Slider(frame, height=30, width=50).place()

    sleep(2)
    btn.place(40, 0)
    sleep(2)
    frame.place(20, 20)
    sleep(1)
    frame.hide()
    sleep(1)
    frame.show()
    sleep(1)
    btn.hide()
    sleep(1)
    frame.hide()
    sleep(1)
    frame.show()
    sleep(1)
    btn.show()


if __name__ == "__main__":
    __main__()
