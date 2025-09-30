#!/usr/bin/env python3

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import VSplit, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding import KeyBindings

import duden

logfile = open("log.txt", "a")


def log(*args):
    print(*args, file=logfile)
    logfile.flush()


kb = KeyBindings()


@kb.add("c-c")
def exit(event):
    event.app.exit()


@kb.add("enter")
def confirm(event):
    """
    Pressing Ctrl-Q will exit the user interface.

    Setting a return value means: quit the event loop that drives the user
    interface and return this value from the `Application.run()` call.
    """
    # ftc.text = "Hallo"
    word = duden.get(buffer1.text)
    if word is None:
        ftc.text = "Not found"
    else:
        ftc.text = str(word.title)


buffer1 = Buffer()  # Editable buffer.

ftc = FormattedTextControl(text=".")

root_container = HSplit(
    [
        # One window that holds the BufferControl with the default buffer on
        # the left.
        Window(content=BufferControl(buffer=buffer1), height=1),
        # Display the text 'Hello world' on the right.
        Window(content=ftc),
    ]
)


layout = Layout(root_container)

app = Application(layout=layout, full_screen=False, key_bindings=kb)
app.run()
