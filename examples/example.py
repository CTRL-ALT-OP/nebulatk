import nebulatk as ntk

ntk.animation_controller


def __main__():
    canvas = ntk.Window()
    ntk.Frame(
        canvas, image="examples/Images/background.png", width=500, height=500
    ).place(0, 0)
    # Button(canvas,10,10,text="hahah").place()
    # Button(canvas,text="hahah").place(50,10)
    # Button(canvas,text="hihih", font = ("Helvetica",36)).place(100,100)
    ntk.Button(
        canvas,
        text="hillo",
        fill=[255, 66, 66, 15],
        width=100,
        height=100,
        image="examples/Images/main_button_inactive.png",
        active_image="examples/Images/main_button_inactive2.png",
        hover_image="examples/Images/main_button_active.png",
        active_hover_image="examples/Images/main_button_active2.png",
        mode="toggle",
    ).place(0, 0)
    ntk.Button(
        canvas,
        text="hi",
        font=("Helvetica", 50),
        fill=[255, 67, 67, 45],
    ).place(0, 400)
    # ImageButton(canvas,image="Images/test_inactive.png",active_image="Images/test_active.png").place(0,0)
    # btn_4 = Button(canvas,15,15,text="hahah").place(15,15)
    # btn_4.place(50,60)

    # Frame(canvas,30,30, border = "green").place(160,80)


if __name__ == "__main__":
    __main__()
