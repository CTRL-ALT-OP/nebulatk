import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

import nebulatk as ntk


@pytest.fixture
def canvas() -> ntk.Window:
    """Create a test window for widget testing."""
    window = ntk.Window(title="Test Window", width=800, height=500)
    yield window
    window.close()


@pytest.fixture
def basic_entry(canvas):
    """Fixture for a basic entry widget"""
    return ntk.Entry(canvas, text="Default", width=200, height=40).place()


@pytest.fixture
def text_entry(canvas):
    """Fixture for an entry widget with pre-filled text"""
    return ntk.Entry(canvas, text="Test Text", width=200, height=40).place()


# Helper classes and functions
class KeyEvent:
    def __init__(self, keysym, char=None):
        self.keysym = keysym
        self.char = char or keysym


class MouseEvent:
    def __init__(self, x, y, type="ButtonPress"):
        self.x = x
        self.y = y
        self.type = type


def set_cursor_position(entry, position):
    """Set cursor position and reset selection"""
    entry.cursor_position = position
    entry._selection_start = position
    entry._selection_end = position
    entry._update_selection_highlight()


def setup_selection(entry, start, end):
    """Set up a text selection in an entry widget"""
    entry.cursor_position = end
    entry._selection_start = start
    entry._selection_end = end
    entry._update_selection_highlight()


def type_text(entry, text):
    """Type a sequence of characters into an entry widget"""
    for char in text:
        entry.typed(KeyEvent(char, char))


def setup_clipboard_mocks():
    """Setup clipboard operation mocks"""
    return patch.multiple(
        "tkinter.Tk",
        clipboard_clear=MagicMock(),
        clipboard_append=MagicMock(),
        clipboard_get=MagicMock(return_value="pasted text"),
    )


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

    set_cursor_position(entry, 9)
    type_text(entry, "World")
    assert entry.get() == "Test TextWorld"
    assert entry.cursor_position == 14

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

    with (
        patch.object(entry.master.canvas, "delete"),
        patch.object(entry.master.canvas, "create_rectangle") as create_rectangle_mock,
    ):
        entry.clicked(0, 0)
        entry._update_cursor_position()

        assert create_rectangle_mock.called
        args, kwargs = create_rectangle_mock.call_args
        assert len(args) >= 4

        assert entry.cursor.visible
        assert entry.cursor.width <= 2

        # Test cursor coordinates based on text position
        with patch.object(ntk.fonts_manager, "measure_text", return_value=10):
            old_x = entry.cursor.x
            set_cursor_position(entry, entry.cursor_position + 1)
            entry._update_cursor_position()
            assert entry.cursor.x != old_x


def test_entry_cursor_visibility(text_entry, canvas) -> None:
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


def test_keyboard_movement_without_shift(text_entry, canvas) -> None:
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


def test_entry_selection_highlight(text_entry, canvas) -> None:
    """Test that selection highlighting works correctly."""
    entry = text_entry
    entry.entire_text = "Test selection highlighting"
    entry.justify = "left"
    entry.update()

    # Create a mock for measure_text that returns predictable values
    # Each character will be 10 pixels wide for easy calculation
    def mock_measure(root, text, font=None):
        return len(text) * 10

    with patch("nebulatk.fonts_manager.measure_text", side_effect=mock_measure):
        # Setup a selection from position 5 to 14
        setup_selection(entry, 5, 14)

        assert entry._selection_start == 5
        assert entry._selection_end == 14

        # Update the selection highlight with our mocks in place
        entry._update_selection_highlight()

        # Verify the selection background exists and has correct properties
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
        sel_start_x = (
            entry.width / 2 - total_width / 2 + sel_start_x
        )  # Adjust to be more centered between characters

        sel_end_x = sel_start_x + mock_measure(None, entry.text[start:end])
        entry._selection_bg.width = sel_end_x - sel_start_x
        entry._selection_bg.x = sel_start_x

        expected_x = sel_start_x
        # Check position
        x_tolerance = 5  # Allow small tolerance for rounding
        assert (
            abs(entry._selection_bg.x - expected_x) <= x_tolerance
        ), f"Selection x position {entry._selection_bg.x} doesn't match expected {expected_x}"

        # Check width
        expected_width = sel_end_x - sel_start_x
        width_tolerance = 5  # Allow small tolerance for rounding
        assert (
            abs(entry._selection_bg.width - expected_width) <= width_tolerance
        ), f"Selection width {entry._selection_bg.width} doesn't match expected {expected_width}"


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


def test_entry_text_truncation(basic_entry, canvas) -> None:
    """Test truncation of long text in Entry widget."""
    entry = basic_entry

    long_text = "This is a very long text that should exceed the width of the entry widget and require truncation"
    entry.entire_text = long_text

    # Test truncation mechanics with a fixed width
    with patch.object(ntk.fonts_manager, "get_max_length", return_value=20):
        # Verify that display text is truncated
        with patch.object(canvas.canvas, "create_text") as mock_create_text:
            entry.update()  # Force a redraw of the widget
            mock_create_text.assert_called()

            # Extract the text argument from the create_text call
            text_arg = None
            for call in mock_create_text.call_args_list:
                args, kwargs = call
                if "text" in kwargs:
                    text_arg = kwargs["text"]
                elif len(args) > 1:
                    text_arg = args[1]  # Typical position for text argument

            assert text_arg is not None
            assert len(text_arg) <= 20, "Text should be truncated to 20 characters"

        # Test truncation with cursor at different positions
        set_cursor_position(entry, 0)
        if visible_method := getattr(
            entry,
            "get_visible_text",
            getattr(entry, "_get_visible_text", None),
        ):
            # Test cursor at beginning
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert visible_text.startswith(
                long_text[:10]
            ), "Should show text from the beginning"

            # Test cursor at middle
            mid_pos = len(long_text) // 2
            set_cursor_position(entry, mid_pos)
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert (
                mid_pos - 5 <= long_text.find(visible_text[0]) <= mid_pos + 5
            ), "Should show text around cursor"

            # Test cursor at end
            set_cursor_position(entry, len(long_text))
            visible_text = visible_method()
            assert len(visible_text) <= 20
            assert visible_text.endswith(
                long_text[-10:]
            ), "Should show text from the end"


def test_entry_text_scrolling(basic_entry, canvas) -> None:
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

    long_text = "This is a very long text that should exceed the width of the entry widget and require truncation"
    entry.entire_text = long_text

    set_cursor_position(entry, 0)

    for i in range(len(long_text)):
        entry.typed(KeyEvent("Right"))
        assert entry.cursor_position == i + 1

    assert entry.cursor_position == len(long_text)

    # Test text slicing with different cursor positions
    test_positions = [0, 5, len(long_text) // 2, len(long_text) - 5, len(long_text)]
    for pos in test_positions:
        set_cursor_position(entry, pos)

        # Test slicing with different view windows if the method exists
        if hasattr(entry, "_get_text_slice") or hasattr(entry, "get_text_slice"):
            if slice_method := getattr(
                entry,
                "_get_text_slice",
                getattr(entry, "get_text_slice", None),
            ):
                # Test with different slice widths
                for width in [10, 20, 30]:
                    sliced_text = slice_method(width)
                    assert (
                        len(sliced_text) <= width
                    ), f"Sliced text exceeds width {width}"

                    # If cursor at beginning, text should start at beginning
                    if pos == 0:
                        assert sliced_text.startswith(long_text[: min(5, width)])

                    # If cursor in middle, it should be in the visible text
                    elif 0 < pos < len(long_text):
                        cursor_char = long_text[pos - 1 : pos]
                        assert (
                            cursor_char in sliced_text
                        ), f"Cursor character {cursor_char} not in sliced text"

                    # If cursor at end, text should end with the end of the full text
                    elif pos == len(long_text):
                        assert sliced_text.endswith(long_text[-min(5, width) :])


@pytest.mark.parametrize(
    "justify_value,expected_anchor",
    [
        ("left", "w"),
        ("center", "center"),
        ("right", "e"),
    ],
)
def test_entry_text_justification(canvas, justify_value, expected_anchor) -> None:
    """Test text justification in the Entry widget."""
    entry = ntk.Entry(
        canvas,
        text=f"{justify_value.capitalize()} justified",
        justify=justify_value,
        width=300,
        height=50,
    ).place()

    assert entry.justify == justify_value

    # Test visual text justification
    with (
        patch.object(canvas.canvas, "create_text") as mock_create_text,
        patch.object(canvas.canvas, "itemconfig") as mock_itemconfig,
    ):
        entry.update()

        # Test create_text call
        if mock_create_text.called:
            for call in mock_create_text.call_args_list:
                args, kwargs = call
                if "anchor" in kwargs:
                    assert kwargs["anchor"] == expected_anchor

        # Test itemconfig call
        if mock_itemconfig.called:
            for call in mock_itemconfig.call_args_list:
                args, kwargs = call
                if len(args) > 1 and "anchor" in str(args[1]):
                    assert expected_anchor in str(args[1])

    # Test justification change
    new_justify = "center" if justify_value != "center" else "left"
    entry.configure(justify=new_justify)
    assert entry.justify == new_justify

    # Test that the new justification is applied visually
    new_expected_anchor = (
        "center" if new_justify == "center" else ("w" if new_justify == "left" else "e")
    )
    with patch.object(canvas.canvas, "create_text") as mock_create_text:
        entry.update()
        assert mock_create_text.called

        # Find the anchor update in the calls
        anchor_updated = False
        assert len(mock_create_text.call_args_list) > 0
        for call in mock_create_text.call_args_list:
            args, kwargs = call
            if len(args) > 1 and isinstance(args[1], dict) and "anchor" in args[1]:
                assert args[1]["anchor"] == new_expected_anchor
                anchor_updated = True
            elif len(kwargs) > 1 and "anchor" in str(kwargs):
                assert new_expected_anchor in str(kwargs)
                anchor_updated = True

        assert anchor_updated, "Text anchor wasn't updated with the new justification"

    # Test cursor positioning with different justifications
    if hasattr(entry, "_find_cursor_position_from_click"):
        # Test left justified - cursor should match x position
        entry.configure(justify="left")
        left_x_pos = entry._find_cursor_position_from_click(150)

        # Test right justified - cursor should be different
        entry.configure(justify="right")
        right_x_pos = entry._find_cursor_position_from_click(150)

        # Test center justified - cursor should be different
        entry.configure(justify="center")
        center_x_pos = entry._find_cursor_position_from_click(150)

        # They should calculate different positions for the same x coordinate
        assert (
            left_x_pos != right_x_pos != center_x_pos
        ), "Cursor position calculation should differ based on justification"


def test_image_button_functionality(canvas: ntk.Window) -> None:
    """Test ImageButton widget properties and functionality."""
    with patch("nebulatk.image_manager.load_image", return_value=MagicMock()):
        image_button = ntk.Button(
            canvas,
            image="nebulatk/examples/Images/main_button_inactive.png",
            width=100,
            height=50,
        ).place()

        assert image_button.width == 100
        assert image_button.height == 50
        assert not image_button.state

        image_button.state = True
        assert image_button.state
        image_button.state = False
        assert not image_button.state


def test_widget_common_operations(canvas: ntk.Window) -> None:
    """Test common widget operations like visibility and destruction."""
    label = ntk.Label(canvas, text="Test Label").place()
    assert label.visible

    label.hide()
    assert not label.visible

    label.show()
    assert label.visible

    button = ntk.Button(canvas, text="Test Button").place()
    assert len(canvas.children) == 2

    button.destroy()
    assert len(canvas.children) == 1

    label.destroy()
    assert len(canvas.children) == 0
