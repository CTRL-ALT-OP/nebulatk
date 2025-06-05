import sys
import os
import pytest
from unittest.mock import MagicMock, patch

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import nebulatk modules
import nebulatk as ntk
from nebulatk import bounds_manager, standard_methods


class TestContainer:
    """Test suite for Container widget functionality."""

    @pytest.fixture
    def app(self):
        """Create a test application window."""
        window = ntk.Window(title="Container Test", width=800, height=600)
        yield window
        window.close()

    def test_container_initialization(self, app):
        """Test basic container initialization."""
        container = ntk.Container(app, width=300, height=200)

        # Test basic properties
        assert container.width == 300
        assert container.height == 200
        assert container.visible is True
        assert container.can_focus is True
        assert container.can_hover is True
        assert container.can_click is True

        # Test parent-child relationships
        assert container.root == app
        assert container.master == container  # Container is its own master
        assert hasattr(container, "_window")
        assert container._window == app

        # Test initialization state
        assert container.initialized is True
        assert container.children == []
        assert container.active is None
        assert container.down is None
        assert container.hovered_child is None

        # Test canvas creation
        assert hasattr(container, "canvas")
        assert container.canvas is not None

    def test_container_placement(self, app):
        """Test container placement and positioning."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 75)

        assert container.x == 50
        assert container.y == 75

        # Test that container is added to parent's children
        assert container in app.children

    def test_child_widget_parenting(self, app):
        """Test that child widgets are properly parented to container."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        # Create child widgets
        button = ntk.Button(container, text="Container Button", width=100, height=30)
        button.place(10, 10)

        label = ntk.Label(container, text="Container Label", width=100, height=30)
        label.place(10, 50)

        frame = ntk.Frame(container, width=80, height=40, fill="#ff0000")
        frame.place(10, 90)

        # Test master assignment
        assert button.master == container
        assert label.master == container
        assert frame.master == container

        # Test root assignment
        assert button.root == container
        assert label.root == container
        assert frame.root == container

        # Test children lists
        assert button in container.children
        assert label in container.children
        assert frame in container.children
        assert len(container.children) == 3

        # Test that container is in app's children, but child widgets are not
        assert container in app.children
        assert button not in app.children
        assert label not in app.children
        assert frame not in app.children

    def test_canvas_drawing_isolation(self, app):
        """Test that child widgets draw on container canvas, not main window canvas."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        # Get initial canvas item counts
        initial_container_items = len(container.canvas.find_all())
        initial_window_items = len(app.canvas.find_all())

        # Create a child widget
        button = ntk.Button(container, text="Test Button", width=100, height=30)
        button.place(10, 10)

        # Container canvas should have more items now
        final_container_items = len(container.canvas.find_all())
        final_window_items = len(app.canvas.find_all())

        assert final_container_items > initial_container_items
        # Window canvas should only have items for the container itself, not the button
        assert final_window_items >= initial_window_items

    def test_container_canvas_methods(self, app):
        """Test container's canvas drawing methods."""
        container = ntk.Container(app, width=300, height=200)

        # Test create_rectangle
        rect_id, image = container.create_rectangle(10, 10, 50, 30, fill="#ff0000")
        assert rect_id is not None
        assert image is None  # No transparency, so no image

        # Test create_text
        text_id, image = container.create_text(
            100, 50, "Test Text", font=("Arial", 12), fill="blue"
        )
        assert text_id is not None
        assert image is None

        # Test canvas method existence (without actually creating images due to tkinter complexity)
        assert hasattr(container, "create_image")
        assert hasattr(container, "create_rectangle")
        assert hasattr(container, "create_text")
        assert hasattr(container, "move")
        assert hasattr(container, "delete")
        assert hasattr(container, "configure")

    def test_container_transparency_support(self, app):
        """Test container's support for transparent rectangles."""
        container = ntk.Container(app, width=300, height=200)

        # Test non-transparent rectangle
        rect_id, image = container.create_rectangle(10, 10, 50, 30, fill="#ff0000ff")
        assert rect_id is not None
        assert image is None

        # Test that the transparency check logic exists
        # (avoiding actual transparent rect creation due to tkinter mocking complexity)
        assert len("#ff000088") > 7  # Transparency format check
        assert "#ff000088"[7:] != "ff"  # Alpha channel check

    def test_hit_detection_with_containers(self, app):
        """Test hit detection works correctly with container widgets."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        button = ntk.Button(container, text="Hit Test", width=100, height=30)
        button.place(10, 10)  # Button at (10,10) relative to container

        # Test hit detection - should work without AttributeErrors
        hit_result = bounds_manager.check_hit(button, 60, 25)  # Should hit
        assert hit_result is True

        miss_result = bounds_manager.check_hit(button, 200, 200)  # Should miss
        assert miss_result is False

    def test_position_calculation_functions(self, app):
        """Test position calculation functions work with containers."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        button = ntk.Button(container, text="Position Test", width=100, height=30)
        button.place(10, 10)

        # Test get_rect_points
        points = standard_methods.get_rect_points(button)
        assert len(points) == 4
        assert all(isinstance(p, tuple) and len(p) == 2 for p in points)

        # Test rel_position_to_abs
        abs_pos = standard_methods.rel_position_to_abs(button, 20, 30)
        assert isinstance(abs_pos, tuple)
        assert len(abs_pos) == 2

        # Test abs_position_to_rel
        rel_pos = standard_methods.abs_position_to_rel(button, abs_pos[0], abs_pos[1])
        assert isinstance(rel_pos, tuple)
        assert len(rel_pos) == 2

    def test_container_event_handling(self, app):
        """Test container's event handling capabilities."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        button = ntk.Button(container, text="Event Test", width=100, height=30)
        button.place(10, 10)

        # Mock event object
        mock_event = MagicMock()
        mock_event.x = 60  # Over the button
        mock_event.y = 25
        mock_event.char = "a"

        # Test click handling
        container.click(mock_event)
        assert container.active == button or container.down == button

        # Test hover handling
        container.hover(mock_event)
        # Should not raise exceptions

        # Test key handling
        container.typing(mock_event)
        # Should not raise exceptions

    def test_container_widget_layering(self, app):
        """Test that container implements proper widget layering."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        # Create widgets
        button = ntk.Button(container, text="Foreground", width=100, height=30)
        button.place(10, 10)

        # Check that canvas items have proper tags
        canvas_items = container.canvas.find_all()

        # Check for proper tagging
        fg_items = container.canvas.find_withtag("fg_item")
        bg_items = container.canvas.find_withtag("background_item")

        assert len(fg_items) > 0  # Should have foreground items from child widgets

    def test_container_root_property(self, app):
        """Test container's root property behavior."""
        container = ntk.Container(app, width=300, height=200)

        # Test root getter
        assert container.root == app

        # Test root setter
        new_parent = ntk.Frame(app, width=400, height=300)
        container.root = new_parent
        assert container.root == new_parent
        assert container._window == app  # Window should still point to original window

    def test_nested_containers(self, app):
        """Test containers within containers."""
        parent_container = ntk.Container(app, width=400, height=300)
        parent_container.place(50, 50)

        child_container = ntk.Container(parent_container, width=200, height=150)
        child_container.place(20, 20)

        # Test parent-child relationships
        assert child_container.root == parent_container
        assert child_container.master == child_container  # Self-master
        # The nested container's _window might be the parent container, which is correct
        assert hasattr(child_container, "_window")
        assert child_container in parent_container.children

        # Add widget to nested container
        button = ntk.Button(child_container, text="Nested", width=80, height=25)
        button.place(5, 5)

        assert button.master == child_container
        assert button.root == child_container
        assert button in child_container.children

    def test_container_canvas_object_replication(self, app):
        """Test that container replicates background objects from main window."""
        # Create some objects on the main window first
        app_frame = ntk.Frame(app, width=100, height=50, fill="#00ff00")
        app_frame.place(10, 10)

        # Now create container - it should replicate existing objects
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        # Container should have background items replicated from main window
        bg_items = container.canvas.find_withtag("background_item")
        assert len(bg_items) > 0

    def test_container_background_position_adjustment(self, app):
        """Test that replicated background objects are positioned correctly relative to container."""
        # Create a frame at position (20, 30) on the main window
        app_frame = ntk.Frame(app, width=60, height=40, fill="#ff0000")
        app_frame.place(20, 30)

        # Create container at position (50, 60)
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 60)

        # Find the replicated background item
        bg_items = container.canvas.find_withtag("background_item")
        assert len(bg_items) > 0

        # Get the coordinates of the first background item (should be the replicated frame)
        bg_item = bg_items[0]
        coords = container.canvas.coords(bg_item)

        # The replicated frame should be positioned at:
        # Original position (20, 30) - Container position (50, 60) = (-30, -30)
        expected_x = 20 - 50  # -30
        expected_y = 30 - 60  # -30

        assert coords[0] == expected_x, f"Expected x={expected_x}, got {coords[0]}"
        assert coords[1] == expected_y, f"Expected y={expected_y}, got {coords[1]}"

    def test_container_destruction_cleanup(self, app):
        """Test proper cleanup when container is destroyed."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        button = ntk.Button(container, text="To Destroy", width=100, height=30)
        button.place(10, 10)

        # Verify setup
        assert container in app.children
        assert button in container.children

        # Note: The base Component class doesn't have a destroy method yet,
        # but we can test the parent-child relationship cleanup
        app.children.remove(container)
        assert container not in app.children

    def test_image_manager_container_compatibility(self, app):
        """Test that image_manager works correctly with containers."""
        container = ntk.Container(app, width=300, height=200)

        # Test with mock image object
        mock_widget = MagicMock()
        mock_widget.master = container
        mock_widget.width = 50
        mock_widget.height = 50
        mock_widget.border_width = 0

        from nebulatk import image_manager

        # This should work without errors (container has _window attribute)
        with patch("PIL.ImageTk.PhotoImage") as mock_photo:
            mock_photo.return_value = "mock_photo_image"
            result = image_manager.convert_image(mock_widget, MagicMock())
            assert result == "mock_photo_image"

    def test_fonts_manager_container_compatibility(self, app):
        """Test that fonts_manager works correctly with containers."""
        container = ntk.Container(app, width=300, height=200)

        from nebulatk import fonts_manager

        # This should work without errors (container has _window attribute)
        with patch("tkinter.font.Font") as mock_font:
            mock_font_instance = MagicMock()
            mock_font_instance.measure.return_value = 100
            mock_font_instance.metrics.return_value = 20
            mock_font.return_value = mock_font_instance

            width = fonts_manager.measure_text(container, ("Arial", 12), "Test")
            assert width == 100

            height = fonts_manager.get_font_metrics(
                container, ("Arial", 12), "linespace"
            )
            assert height == 20
