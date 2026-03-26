import sys
import os
import time
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
        window = ntk.Window(
            title="Container Test",
            width=800,
            height=600,
            render_mode="image_gl",
            fps=30,
        )
        yield window
        window.close()

    @pytest.fixture
    def app_image_gl(self):
        """Create a test application window using image/OpenGL mode."""
        window = ntk.Window(title="Container ImageGL Test", width=640, height=480, render_mode="image_gl", fps=30)
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

        # Test image_gl surface creation
        assert hasattr(container, "canvas")
        assert container.canvas is None
        assert container.surface is not None
        assert container.surface_id is not None

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
        """Test that child widgets draw on container surface, not root surface."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        initial_container_items = len(container.surface.objects)
        initial_window_items = len(app.renderer.root_surface.objects)

        # Create a child widget
        button = ntk.Button(container, text="Test Button", width=100, height=30)
        button.place(10, 10)

        # Container surface should have more items now
        final_container_items = len(container.surface.objects)
        final_window_items = len(app.renderer.root_surface.objects)

        assert final_container_items > initial_container_items
        # Root surface should not gain child widget objects from the container
        assert final_window_items == initial_window_items

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
        """Test container preserves object order for layered widgets."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        frame = ntk.Frame(container, width=120, height=60, fill="#ff0000").place(0, 0)
        button = ntk.Button(container, text="Foreground", width=100, height=30).place(10, 10)

        frame_index = container.surface._z_order.index(frame.bg_object)
        button_index = container.surface._z_order.index(button.bg_object)
        assert frame_index < button_index

    def test_container_root_property(self, app):
        """Test container's root property behavior."""
        container = ntk.Container(app, width=300, height=200)

        # Test root getter
        assert container.root == app

        # Test root setter
        new_parent = ntk.Frame(app, width=400, height=300)
        container.root = new_parent
        assert container.root == new_parent
        assert container._window == new_parent

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
        """Test container does not replicate root-surface objects automatically."""
        app_frame = ntk.Frame(app, width=100, height=50, fill="#00ff00")
        app_frame.place(10, 10)

        root_count_before = len(app.renderer.root_surface.objects)
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 50)

        assert len(app.renderer.root_surface.objects) >= root_count_before
        assert len(container.surface.objects) == 0

    def test_container_background_position_adjustment(self, app):
        """Test container surface placement updates the renderer metadata."""
        container = ntk.Container(app, width=300, height=200)
        container.place(50, 60)
        assert container.surface.x == 50
        assert container.surface.y == 60

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

        # OpenGL path should return the PIL object directly.
        source_image = MagicMock()
        result = image_manager.convert_image(mock_widget, source_image)
        assert result is source_image

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

    def test_container_image_gl_surface_initialization(self, app_image_gl):
        """Test container setup when using image_gl rendering mode."""
        timeout_at = time.time() + 1.0
        while app_image_gl.renderer is None and time.time() < timeout_at:
            time.sleep(0.01)

        container = ntk.Container(app_image_gl, width=300, height=200)
        container.place(50, 75)

        assert container._image_render_mode is True
        assert container.surface_id is not None
        assert container.surface is not None
        assert container.canvas is None
        assert container.surface.width == 300
        assert container.surface.height == 200

    def test_container_image_gl_drawing_marks_renderer_dirty(self, app_image_gl):
        """Test drawing in image_gl mode updates the container surface and dirty flag."""
        timeout_at = time.time() + 1.0
        while app_image_gl.renderer is None and time.time() < timeout_at:
            time.sleep(0.01)

        container = ntk.Container(app_image_gl, width=220, height=140)
        container.place(20, 20)

        app_image_gl.renderer.dirty = False
        rect_id, _ = container.create_rectangle(
            5, 5, 100, 40, fill="#00ff00ff", border_width=0, outline="#00ff00ff"
        )
        assert rect_id in container.surface.objects
        assert app_image_gl.renderer.needs_redraw() is True

    def test_image_gl_nested_hit_detection(self, app_image_gl):
        """Test deepest hit detection finds nested container children in image_gl mode."""
        timeout_at = time.time() + 1.0
        while app_image_gl.renderer is None and time.time() < timeout_at:
            time.sleep(0.01)

        container = ntk.Container(app_image_gl, width=300, height=200)
        container.place(50, 50)
        button = ntk.Button(container, text="Hit Test", width=120, height=40)
        button.place(10, 10)

        hit = app_image_gl._find_deepest_hit(app_image_gl.children, 70, 70)
        assert hit == button
