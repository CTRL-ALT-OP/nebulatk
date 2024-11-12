# THIS PROJECT IS CURRENTLY IN EARLY DEVELOPMENT
# FEEL FREE TO USE, REPORT ALL UNEXPECTED BEHAVIORS, QUESTIONS, OR FEATURE REQUESTS TO:
# ctrl.alt.op@gmail.com

NebulaTk is a wrapper of Tkinter that implements many functions that Tkinter does not.
Currently, it exclusively uses the tcl Canvas widget to display visuals, to allow for full transparency support.
All events, widgets, and functionality has been written either custom or with Pillow.


## Non-TCL functionality:
1. Non-blocking window mainloop
2. One-line support
    1. Multiple functions can be chained together, e.g. "Button().place().hide()"
    2. Window creation is done in one line
3. Window uses similar syntax to widgets
    1. Configuration of the window is done as arguments in creation. E.g. "Window(title="test")"
    2. Most methods that are in widgets, like .place() are also valid methods in the window
4. Simple image loading, powered by Pillow
    1. Images are passed in simply as paths, and are automatically loaded in, and resized according to the widget size
    2. Full transparency support
    3. Automatic boundaries for images with transparent portions
    4. Different images for different widget states are supported
5. Default behaviour for everything
6. TTF files can be loaded and used as fonts, without having to install them
7. Text is automatically resized to fit the widget, unless specified