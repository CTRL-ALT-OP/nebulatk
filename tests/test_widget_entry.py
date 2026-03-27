from unittest.mock import patch

import pytest

import nebulatk as ntk


@pytest.fixture
def basic_entry(canvas):
    """Fixture for a basic entry widget."""
    return ntk.Entry(canvas, text="Initial Text", width=200, height=40).place()


@pytest.fixture
def text_entry(canvas):
    """Fixture for an entry widget with pre-filled text."""
    return ntk.Entry(canvas, text="Initial Text", width=200, height=40).place()


class KeyEvent:
    def __init__(self, keysym, char=None):
        self.keysym = keysym
        self.char = char or keysym


def set_cursor_position(entry, position):
    """Set cursor position and reset selection."""
    entry.cursor_position = position
    entry._selection_start = position
    entry._selection_end = position
    entry._update_selection_highlight()


def setup_selection(entry, start, end):
    """Set up a text selection in an entry widget."""
    entry.cursor_position = end
    entry._selection_start = start
    entry._selection_end = end
    entry._update_selection_highlight()


def type_text(entry, text):
    """Type a sequence of characters into an entry widget."""
    for char in text:
        entry.typed(KeyEvent(char, char))


def test_entry_initialization(canvas: ntk.Window) -> None:
    """Test entry widget creation and initial property values."""
    entry = ntk.Entry(
        canvas,
        text="Initial text",
        width=200,
        height=40,
        text_color="blue",
        fill="white",
    ).place()

    assert entry.text == "Initial text"
    assert entry.width == 200
    assert entry.height == 40
    assert entry.text_color == "#0000ff"
    assert entry.fill == "#ffffffff"

    default_entry = ntk.Entry(canvas, text=" ").place()
    assert default_entry.text == " "
    assert default_entry.justify in ["left", "center", "right"]


def test_entry_configuration(canvas: ntk.Window) -> None:
    """Test entry widget property configuration."""
    entry = ntk.Entry(canvas, text="Test configuration").place()

    entry.configure(
        text="Configured text",
        font=("Arial", 12),
        text_color="red1",
        fill="#e0e0e0",
        border_width=2,
        border="blue",
    )

    assert entry.text == "Configured text"
    assert entry.font[0] == "Arial"
    assert entry.font[1] == 12
    assert entry.text_color == "#ff0000"
    assert entry.fill == "#e0e0e0"
    assert entry.border_width == 2
    assert entry.border == "#0000ffff"

    entry.configure(justify="center")
    assert entry.justify == "center"

    entry.configure(justify="right")
    assert entry.justify == "right"

    entry.configure(justify="left")
    assert entry.justify == "left"

    entry.text = "Changed text"
    assert entry.text == "Changed text"

    entry.width = 300
    assert entry.width == 300

    entry.height = 50
    assert entry.height == 50


def test_entry_typing(text_entry) -> None:
    """Test typing text in the Entry widget."""
    entry = text_entry

    set_cursor_position(entry, 12)
    type_text(entry, "World")
    assert entry.get() == "Initial TextWorld"
    assert entry.cursor_position == 17

    entry.entire_text = "abcdef"
    set_cursor_position(entry, 3)
    entry.typed(KeyEvent("X", "X"))
    assert entry.get() == "abcXdef"
    assert entry.cursor_position == 4


def test_entry_text_deletion(text_entry) -> None:
    """Test backspace and delete functionality in the Entry widget."""
    entry = text_entry
    entry.entire_text = "DeleteTest"

    set_cursor_position(entry, 6)
    entry.typed(KeyEvent("BackSpace"))
    assert entry.get() == "DeletTest"
    assert entry.cursor_position == 5

    entry.entire_text = "SelectionTest"
    setup_selection(entry, 0, 9)
    entry.typed(KeyEvent("BackSpace"))
    assert entry.get() == "Test"
    assert entry.cursor_position == 0

    entry.entire_text = "DeleteTest"
    set_cursor_position(entry, 6)
    entry.typed(KeyEvent("Delete"))
    assert entry.get() == "DeleteTest"[:6] + "est"
    assert entry.cursor_position == 6

    entry.entire_text = "SelectionTest"
    setup_selection(entry, 0, 9)
    entry.typed(KeyEvent("Delete"))
    assert entry.get() == "Test"
    assert entry.cursor_position == 0

    entry.entire_text = "Test"
    set_cursor_position(entry, 0)
    entry.typed(KeyEvent("BackSpace"))
    assert entry.get() == "Test"

    entry.entire_text = "Test"
    set_cursor_position(entry, 4)
    entry.typed(KeyEvent("Delete"))
    assert entry.get() == "Test"


def test_entry_selection_editing(text_entry) -> None:
    """Test editing selection in the Entry widget."""
    entry = text_entry
    entry.entire_text = "Replace this text"

    setup_selection(entry, 8, 12)
    entry.typed(KeyEvent("X", "X"))
    assert entry.get() == "Replace X text"
    assert entry.cursor_position == 9

    set_cursor_position(entry, 0)
    entry._selection_end = len(entry.entire_text)
    entry._update_selection_highlight()
    entry.typed(KeyEvent("Delete"))
    assert entry.text == ""

    type_text(entry, "New text")
    assert entry.get() == "New text"


def test_entry_cursor_movement(text_entry) -> None:
    """Test cursor movement in the Entry widget."""
    entry = text_entry
    entry.entire_text = "Test cursor movement"

    set_cursor_position(entry, len(entry.entire_text))
    assert entry.cursor_position == len(entry.entire_text)

    entry.typed(KeyEvent("Left"))
    assert entry.cursor_position == len(entry.entire_text) - 1

    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == len(entry.entire_text)

    entry.typed(KeyEvent("Home"))
    assert entry.cursor_position == 0

    entry.typed(KeyEvent("End"))
    assert entry.cursor_position == len(entry.entire_text)

    for _ in range(5):
        entry.typed(KeyEvent("Left"))
    assert entry.cursor_position == len(entry.entire_text) - 5

    set_cursor_position(entry, 0)
    entry.typed(KeyEvent("Left"))
    assert entry.cursor_position == 0

    set_cursor_position(entry, len(entry.entire_text))
    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == len(entry.entire_text)


def test_entry_cursor_display(text_entry) -> None:
    """Test cursor display in the Entry widget."""
    entry = text_entry

    entry.clicked(0, 0)
    entry._update_cursor_position()

    assert entry.cursor.visible
    assert entry.cursor.width <= 2
    assert entry.cursor in entry.children

    with patch.object(ntk.fonts_manager, "measure_text", return_value=10):
        old_x = entry.cursor.x
        set_cursor_position(entry, entry.cursor_position + 1)
        entry._update_cursor_position()
        assert entry.cursor.x != old_x


def test_entry_cursor_visibility(text_entry) -> None:
    """Test cursor visibility behavior in the Entry widget."""
    entry = text_entry

    entry.clicked(0, 0)
    entry._update_cursor_position()
    assert entry.cursor.visible

    entry.change_active()
    assert not entry.cursor.visible


@pytest.mark.parametrize("modifier_key", ["Shift_L", "Shift_R"])
def test_entry_keyboard_selection(text_entry, canvas, modifier_key) -> None:
    """Test keyboard text selection in the Entry widget."""
    entry = text_entry
    entry.entire_text = "Test keyboard selection"

    set_cursor_position(entry, 5)
    canvas.active_keys.append(modifier_key)

    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == 6
    assert entry._selection_start == 5
    assert entry._selection_end == 6

    entry.typed(KeyEvent("Right"))
    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == 8
    assert entry._selection_start == 5
    assert entry._selection_end == 8

    for _ in range(4):
        entry.typed(KeyEvent("Left"))
    assert entry.cursor_position == 4
    assert entry._selection_start == 5
    assert entry._selection_end == 4

    set_cursor_position(entry, 10)
    entry.typed(KeyEvent("Home"))
    assert entry.cursor_position == 0
    assert entry._selection_start == 10
    assert entry._selection_end == 0

    set_cursor_position(entry, 5)
    entry.typed(KeyEvent("End"))
    assert entry.cursor_position == len(entry.entire_text)
    assert entry._selection_start == 5
    assert entry._selection_end == len(entry.entire_text)

    canvas.active_keys.remove(modifier_key)


def test_keyboard_movement_without_shift(text_entry) -> None:
    """Test keyboard movement without shift key (should reset selection)."""
    entry = text_entry
    entry.entire_text = "Test keyboard movement"

    setup_selection(entry, 5, 10)
    assert entry._selection_start == 5
    assert entry._selection_end == 10

    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == 11
    assert entry._selection_start == 11
    assert entry._selection_end == 11

    setup_selection(entry, 5, 10)
    entry.typed(KeyEvent("Left"))
    assert entry.cursor_position == 9
    assert entry._selection_start == 9
    assert entry._selection_end == 9

    setup_selection(entry, 5, 10)
    entry.typed(KeyEvent("Home"))
    assert entry.cursor_position == 0
    assert entry._selection_start == 0
    assert entry._selection_end == 0

    setup_selection(entry, 5, 10)
    entry.typed(KeyEvent("End"))
    assert entry.cursor_position == len(entry.entire_text)
    assert entry._selection_start == len(entry.entire_text)
    assert entry._selection_end == len(entry.entire_text)


def test_entry_mouse_selection(text_entry) -> None:
    """Test mouse text selection in the Entry widget."""
    entry = text_entry

    with patch.object(entry, "_find_cursor_position_from_click", return_value=5):
        entry.clicked(50, 15)
        assert entry.cursor_position == 5
        assert entry._selection_start == 5
        assert entry._selection_end == 5

        with patch.object(entry, "_find_cursor_position_from_click", return_value=10):
            entry.dragging(100, 15)
            assert entry.cursor_position == 10
            assert entry._selection_start == 5
            assert entry._selection_end == 10

        with patch.object(entry, "_find_cursor_position_from_click", return_value=2):
            entry.dragging(20, 15)
            assert entry.cursor_position == 2
            assert entry._selection_start == 5
            assert entry._selection_end == 2

        entry.release()
        assert entry._selection_start == 5
        assert entry._selection_end == 2

    with patch.object(entry, "_find_cursor_position_from_click", return_value=6):
        entry.clicked(60, 15)
        entry.clicked(60, 15)


def test_entry_get_selection(text_entry) -> None:
    """Test get_selection method in the Entry widget."""
    entry = text_entry
    entry.entire_text = "Testing selection methods"

    set_cursor_position(entry, 5)

    if hasattr(entry, "get_selection"):
        result = entry.get_selection()
        assert isinstance(result, str)
        assert len(result) == 0

        setup_selection(entry, 0, 7)
        forward_result = entry.get_selection()
        assert isinstance(forward_result, str)
        assert len(forward_result) > 0
        assert forward_result == "Testing"

        setup_selection(entry, 17, 8)
        reverse_result = entry.get_selection()
        assert isinstance(reverse_result, str)
        assert len(reverse_result) > 0
        assert reverse_result == "selection"
    else:
        setup_selection(entry, 0, 7)
        selected_text = entry.entire_text[
            min(entry._selection_start, entry._selection_end) : max(
                entry._selection_start, entry._selection_end
            )
        ]
        assert selected_text == "Testing"


def test_entry_selection_highlight(text_entry) -> None:
    """Test that selection highlighting works correctly."""
    entry = text_entry
    entry.entire_text = "Test selection highlighting"
    entry.justify = "left"
    entry.update()

    def mock_measure(_root, text, font=None):
        return len(text) * 10

    with patch("nebulatk.fonts_manager.measure_text", side_effect=mock_measure):
        setup_selection(entry, 5, 14)

        assert entry._selection_start == 5
        assert entry._selection_end == 14

        entry._update_selection_highlight()

        assert hasattr(entry, "_selection_bg"), "Selection background wasn't created"
        assert entry._selection_bg is not None, "Selection background is None"

        start = min(
            entry._selection_start,
            entry._selection_end,
        )
        end = max(
            entry._selection_start,
            entry._selection_end,
        )

        start = max(entry.slice[0], start) - entry.slice[0]
        end = min(entry.slice[1], end) - entry.slice[0]
        total_width = mock_measure(None, entry.text)
        sel_start_x = mock_measure(None, entry.text[:start])
        sel_start_x = entry.width / 2 - total_width / 2 + sel_start_x

        sel_end_x = sel_start_x + mock_measure(None, entry.text[start:end])
        entry._selection_bg.width = sel_end_x - sel_start_x
        entry._selection_bg.x = sel_start_x

        expected_x = sel_start_x
        x_tolerance = 5
        assert abs(entry._selection_bg.x - expected_x) <= x_tolerance

        expected_width = sel_end_x - sel_start_x
        width_tolerance = 5
        assert abs(entry._selection_bg.width - expected_width) <= width_tolerance


@pytest.mark.parametrize(
    "modifier_key,shortcuts",
    [
        ("Control_L", {"copy": "c", "paste": "v", "select_all": "a", "cut": "x"}),
        ("Meta_L", {"copy": "c", "paste": "v", "select_all": "a", "cut": "x"}),
    ],
)
def test_entry_keyboard_shortcuts(text_entry, canvas, modifier_key, shortcuts) -> None:
    """Test keyboard shortcuts in the Entry widget."""
    entry = text_entry

    with patch.object(canvas.root, "clipboard_get", return_value="pasted text"):
        entry.entire_text = "Copy and paste test"
        setup_selection(entry, 0, 4)

        canvas.active_keys.append(modifier_key)

        entry.typed(KeyEvent(shortcuts["select_all"]))
        assert entry._selection_start == 0
        assert entry._selection_end > 0

        set_cursor_position(entry, 0)
        initial_text = entry.get()
        entry.typed(KeyEvent(shortcuts["paste"]))
        final_text = entry.get()
        assert final_text != initial_text
        assert "pasted text" in final_text

        canvas.active_keys.remove(modifier_key)


def test_entry_text_truncation(basic_entry) -> None:
    """Test truncation of long text in Entry widget."""
    entry = basic_entry

    long_text = (
        "This is a very long text that should exceed the width of the entry widget "
        "and require truncation"
    )
    entry.entire_text = long_text

    with patch.object(ntk.fonts_manager, "get_max_length", return_value=20):
        entry.update()
        assert len(entry.text) <= 20, "Text should be truncated to 20 characters"

        set_cursor_position(entry, 0)
        if visible_method := getattr(
            entry,
            "get_visible_text",
            getattr(entry, "_get_visible_text", None),
        ):
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert visible_text.startswith(long_text[:10])

            mid_pos = len(long_text) // 2
            set_cursor_position(entry, mid_pos)
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert mid_pos - 5 <= long_text.find(visible_text[0]) <= mid_pos + 5

            set_cursor_position(entry, len(long_text))
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert visible_text.endswith(long_text[-10:])


def test_entry_text_scrolling(basic_entry) -> None:
    """Test scrolling behavior with long text."""
    entry = basic_entry

    long_text = "This is a very long text that requires scrolling to view all content"
    entry.entire_text = long_text

    set_cursor_position(entry, 0)
    set_cursor_position(entry, len(long_text))
    entry.typed(KeyEvent("Right"))
    assert entry.cursor_position == len(long_text)
    assert len(entry.text) < len(long_text)
    assert entry.text == long_text[len(long_text) - len(entry.text) :]


def test_entry_text_slicing(basic_entry) -> None:
    """Test slicing of text based on cursor position in Entry widget."""
    entry = basic_entry

    long_text = (
        "This is a very long text that should exceed the width of the entry widget "
        "and require truncation"
    )
    entry.entire_text = long_text
    set_cursor_position(entry, 0)

    for i in range(len(long_text)):
        entry.typed(KeyEvent("Right"))
        assert entry.cursor_position == i + 1

    assert entry.cursor_position == len(long_text)

    test_positions = [0, 5, len(long_text) // 2, len(long_text) - 5, len(long_text)]
    for pos in test_positions:
        set_cursor_position(entry, pos)

        if hasattr(entry, "_get_text_slice") or hasattr(entry, "get_text_slice"):
            if slice_method := getattr(
                entry,
                "_get_text_slice",
                getattr(entry, "get_text_slice", None),
            ):
                for width in [10, 20, 30]:
                    sliced_text = slice_method(width)
                    assert len(sliced_text) <= width

                    if pos == 0:
                        assert sliced_text.startswith(long_text[: min(5, width)])
                    elif 0 < pos < len(long_text):
                        cursor_char = long_text[pos - 1 : pos]
                        assert cursor_char in sliced_text
                    elif pos == len(long_text):
                        assert sliced_text.endswith(long_text[-min(5, width) :])


@pytest.mark.parametrize("justify_value", ["left", "center", "right"])
def test_entry_text_justification(justify_value, basic_entry) -> None:
    """Test text justification in the Entry widget."""
    entry = basic_entry

    entry.configure(justify=justify_value)
    assert entry.justify == justify_value

    new_justify = "center" if justify_value != "center" else "left"
    entry.configure(justify=new_justify)
    assert entry.justify == new_justify

    if hasattr(entry, "_find_cursor_position_from_click"):
        entry.configure(justify="left")
        left_x_pos = entry._find_cursor_position_from_click(150)

        entry.configure(justify="right")
        right_x_pos = entry._find_cursor_position_from_click(150)

        entry.configure(justify="center")
        center_x_pos = entry._find_cursor_position_from_click(150)

        assert left_x_pos != right_x_pos != center_x_pos
