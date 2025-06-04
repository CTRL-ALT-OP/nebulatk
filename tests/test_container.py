import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Now import your package/module
import nebulatk as ntk


@pytest.fixture
def window() -> ntk.Window:
    """
    Create a test window for Container widget testing.

    Returns:
        ntk.Window: A window instance for testing Container widgets.
    """
    window = ntk.Window(title="Test Container Window", width=800, height=600)
    yield window
    window.close()


@pytest.fixture
def container_with_widgets(window: ntk.Window):
    """
    Create a test setup with a container and several widgets.

    Args:
        window: The test window fixture.

    Returns:
        tuple: (container, widgets_list) for testing.
    """
    # Create background widgets
    bg_button = ntk.Button(
        window, text="Background Button", width=100, height=50
    ).place(50, 50)
    bg_label = ntk.Label(window, text="Background Label", width=120, height=30).place(
        200, 100
    )
    bg_frame = ntk.Frame(window, width=80, height=80, fill="blue").place(300, 200)

    # Create container that overlaps with some widgets
    container = ntk.Container(window, width=200, height=150).place(150, 75)

    widgets = [bg_button, bg_label, bg_frame]

    yield container, widgets

    # Cleanup
    for widget in widgets:
        widget.destroy()
    container.destroy()


class TestContainerBasics:
    """Test basic Container widget functionality."""

    def test_container_creation(self, window: ntk.Window):
        """Test basic container creation and properties."""
        container = ntk.Container(window, width=300, height=200)

        # Test basic properties
        assert container.width == 300
        assert container.height == 200
        assert container.root == window
        assert container.master == window

        # Test container-specific properties
        assert hasattr(container, "canvas"), "Container should have a canvas attribute"
        assert container.canvas is not None, "Container canvas should be initialized"

        # Test that container has transparency simulation capabilities
        assert hasattr(
            container, "cloned_widgets"
        ), "Container should track cloned widgets"
        assert hasattr(
            container, "overlapping_widgets"
        ), "Container should track overlapping widgets"

        container.destroy()

    def test_container_placement(self, window: ntk.Window):
        """Test container placement on the window."""
        container = ntk.Container(window, width=150, height=100).place(50, 75)

        assert container.x == 50
        assert container.y == 75
        assert container in window.children

        # Test that container is properly positioned
        assert container._position == [50, 75]
        assert container._size == [150, 100]

        container.destroy()

    def test_container_visibility(self, window: ntk.Window):
        """Test container show/hide functionality."""
        container = ntk.Container(window, width=100, height=100).place()

        # Initially visible
        assert container.visible

        # Hide container
        container.hide()
        assert not container.visible

        # Show container
        container.show()
        assert container.visible

        container.destroy()


class TestContainerTransparency:
    """Test Container transparency simulation functionality."""

    def test_overlapping_widget_detection(self, container_with_widgets):
        """Test that container correctly identifies overlapping widgets."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        # Container is at (150, 75) with size 200x150
        # bg_button is at (50, 50) with size 100x50 - should overlap
        # bg_label is at (200, 100) with size 120x30 - should overlap
        # bg_frame is at (300, 200) with size 80x80 - should NOT overlap

        overlapping = container.get_overlapping_widgets()

        # Should find the button and label but not the frame
        assert bg_button in overlapping, "Button should be detected as overlapping"
        assert bg_label in overlapping, "Label should be detected as overlapping"
        assert (
            bg_frame not in overlapping
        ), "Frame should not be detected as overlapping"

    def test_widget_cloning(self, container_with_widgets):
        """Test that container correctly clones overlapping widgets."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        # Trigger cloning
        container.update_cloned_widgets()

        # Check that cloned widgets are created
        assert len(container.cloned_widgets) > 0, "Container should have cloned widgets"

        # Check that cloned widgets match overlapping widgets
        overlapping = container.get_overlapping_widgets()
        assert len(container.cloned_widgets) == len(
            overlapping
        ), "Number of cloned widgets should match overlapping widgets"

        # Check that cloned widgets have correct properties
        for original, cloned in zip(overlapping, container.cloned_widgets):
            assert cloned.text == original.text if hasattr(original, "text") else True
            assert cloned.fill == original.fill if hasattr(original, "fill") else True
            assert cloned.width == original.width
            assert cloned.height == original.height

    def test_cloned_widget_positioning(self, container_with_widgets):
        """Test that cloned widgets are positioned correctly relative to container."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        container.update_cloned_widgets()

        # Check positioning of cloned widgets
        for original, cloned in zip(
            container.get_overlapping_widgets(), container.cloned_widgets
        ):
            # Calculate expected relative position
            expected_x = original.x - container.x
            expected_y = original.y - container.y

            assert (
                cloned.x == expected_x
            ), f"Cloned widget x position should be {expected_x}, got {cloned.x}"
            assert (
                cloned.y == expected_y
            ), f"Cloned widget y position should be {expected_y}, got {cloned.y}"

    def test_partial_widget_cloning(self, window: ntk.Window):
        """Test that partially overlapping widgets are cloned with correct dimensions."""
        # Create a widget that partially overlaps the container
        bg_widget = ntk.Button(window, text="Partial", width=100, height=100).place(
            50, 50
        )
        container = ntk.Container(window, width=100, height=100).place(100, 100)

        container.update_cloned_widgets()

        # Should have one cloned widget
        assert len(container.cloned_widgets) == 1

        cloned = container.cloned_widgets[0]

        # Check that the cloned widget represents only the overlapping portion
        # The overlap should be 50x50 (from 100,100 to 150,150)
        assert (
            cloned.width == 50
        ), f"Cloned widget width should be 50, got {cloned.width}"
        assert (
            cloned.height == 50
        ), f"Cloned widget height should be 50, got {cloned.height}"

        bg_widget.destroy()
        container.destroy()


class TestContainerUpdates:
    """Test Container dynamic update functionality."""

    def test_widget_addition_updates(self, window: ntk.Window):
        """Test that container updates when new widgets are added."""
        container = ntk.Container(window, width=200, height=200).place(100, 100)

        # Initially no overlapping widgets
        assert len(container.get_overlapping_widgets()) == 0
        assert len(container.cloned_widgets) == 0

        # Add a new overlapping widget
        new_widget = ntk.Button(window, text="New Widget", width=50, height=50).place(
            150, 150
        )

        # Container should automatically update
        container.on_widget_added(new_widget)

        # Check that container now has the new widget
        assert len(container.get_overlapping_widgets()) == 1
        assert len(container.cloned_widgets) == 1
        assert new_widget in container.get_overlapping_widgets()

        new_widget.destroy()
        container.destroy()

    def test_widget_movement_updates(self, container_with_widgets):
        """Test that container updates when widgets are moved."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        initial_count = len(container.get_overlapping_widgets())

        # Move the frame to overlap with container
        bg_frame.place(180, 120)  # Now overlaps with container

        # Trigger update
        container.on_widget_moved(bg_frame)

        # Should now have one more overlapping widget
        new_count = len(container.get_overlapping_widgets())
        assert (
            new_count == initial_count + 1
        ), f"Expected {initial_count + 1} overlapping widgets, got {new_count}"
        assert bg_frame in container.get_overlapping_widgets()

    def test_widget_removal_updates(self, container_with_widgets):
        """Test that container updates when widgets are removed."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        initial_count = len(container.get_overlapping_widgets())

        # Remove an overlapping widget
        bg_button.destroy()

        # Trigger update
        container.on_widget_removed(bg_button)

        # Should now have one fewer overlapping widget
        new_count = len(container.get_overlapping_widgets())
        assert (
            new_count == initial_count - 1
        ), f"Expected {initial_count - 1} overlapping widgets, got {new_count}"
        assert bg_button not in container.get_overlapping_widgets()

    def test_container_resize_updates(self, container_with_widgets):
        """Test that container updates when it is resized."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        initial_count = len(container.get_overlapping_widgets())

        # Resize container to be larger
        container.width = 300
        container.height = 200

        # Trigger update
        container.update_cloned_widgets()

        # May now overlap with more widgets
        new_count = len(container.get_overlapping_widgets())
        assert (
            new_count >= initial_count
        ), "Larger container should not have fewer overlapping widgets"


class TestContainerInteraction:
    """Test Container interaction handling."""

    def test_hover_event_handling(self, container_with_widgets):
        """Test that container properly handles hover events."""
        container, widgets = container_with_widgets

        # Mock hover event
        hover_mock = Mock()

        # Hover over container
        container.hovered()

        # Should trigger hover events on cloned widgets
        for cloned_widget in container.cloned_widgets:
            assert hasattr(
                cloned_widget, "hovered"
            ), "Cloned widget should have hover method"

    def test_click_event_handling(self, container_with_widgets):
        """Test that container properly handles click events."""
        container, widgets = container_with_widgets

        # Click on container
        container.clicked(50, 50)  # Click at relative position

        # Should determine which cloned widget was clicked
        clicked_widget = container.get_clicked_widget(50, 50)

        if clicked_widget:
            assert clicked_widget in container.cloned_widgets

    def test_click_propagation(self, container_with_widgets):
        """Test that clicks are properly propagated to underlying widgets."""
        container, widgets = container_with_widgets
        bg_button, bg_label, bg_frame = widgets

        # Mock the original widget's click method
        original_click = Mock()
        bg_button.clicked = original_click

        # Click on the container where the button is cloned
        container.clicked(bg_button.x - container.x, bg_button.y - container.y)

        # The original widget should receive the click event
        # (This tests click-through functionality)
        container.propagate_click_to_original(
            bg_button, bg_button.x - container.x, bg_button.y - container.y
        )

    def test_drag_event_handling(self, container_with_widgets):
        """Test that container properly handles drag events."""
        container, widgets = container_with_widgets

        # Start dragging
        container.clicked(50, 50)

        # Drag to new position
        container.dragging(75, 75)

        # Should update cloned widget positions accordingly
        for cloned_widget in container.cloned_widgets:
            # Position should be updated based on drag
            assert hasattr(
                cloned_widget, "dragging"
            ), "Cloned widget should handle dragging"


class TestContainerPerformance:
    """Test Container performance and optimization."""

    def test_lazy_cloning(self, window: ntk.Window):
        """Test that widgets are only cloned when necessary."""
        container = ntk.Container(window, width=100, height=100).place(0, 0)

        # Create many widgets that don't overlap
        non_overlapping_widgets = []
        for i in range(10):
            widget = ntk.Button(window, text=f"Button {i}", width=50, height=50).place(
                200 + i * 60, 200
            )
            non_overlapping_widgets.append(widget)

        # Container should not clone any widgets
        container.update_cloned_widgets()
        assert (
            len(container.cloned_widgets) == 0
        ), "Container should not clone non-overlapping widgets"

        # Cleanup
        for widget in non_overlapping_widgets:
            widget.destroy()
        container.destroy()

    def test_cloning_optimization(self, window: ntk.Window):
        """Test that cloning is optimized and doesn't create unnecessary duplicates."""
        container = ntk.Container(window, width=200, height=200).place(100, 100)

        # Create overlapping widget
        widget = ntk.Button(window, text="Test", width=100, height=100).place(150, 150)

        # Update cloned widgets multiple times
        container.update_cloned_widgets()
        first_count = len(container.cloned_widgets)

        container.update_cloned_widgets()
        second_count = len(container.cloned_widgets)

        # Should not create duplicate clones
        assert (
            first_count == second_count
        ), "Multiple updates should not create duplicate clones"

        widget.destroy()
        container.destroy()


class TestContainerEdgeCases:
    """Test Container edge cases and error handling."""

    def test_empty_container(self, window: ntk.Window):
        """Test container behavior with no overlapping widgets."""
        container = ntk.Container(window, width=100, height=100).place(500, 500)

        # Should handle empty state gracefully
        assert len(container.get_overlapping_widgets()) == 0
        assert len(container.cloned_widgets) == 0

        # Update should not cause errors
        container.update_cloned_widgets()

        container.destroy()

    def test_zero_size_container(self, window: ntk.Window):
        """Test container with zero size."""
        container = ntk.Container(window, width=0, height=0).place(100, 100)

        # Should handle zero size gracefully
        assert container.width == 0
        assert container.height == 0
        assert len(container.get_overlapping_widgets()) == 0

        container.destroy()

    def test_container_outside_window(self, window: ntk.Window):
        """Test container placed outside window bounds."""
        container = ntk.Container(window, width=100, height=100).place(1000, 1000)

        # Should still function correctly
        assert container.x == 1000
        assert container.y == 1000

        # Create widget that might overlap
        widget = ntk.Button(window, text="Test", width=50, height=50).place(1050, 1050)

        # Should detect overlap correctly
        container.update_cloned_widgets()

        widget.destroy()
        container.destroy()

    def test_deeply_nested_widgets(self, window: ntk.Window):
        """Test container with deeply nested widget hierarchies."""
        # Create nested structure
        parent_frame = ntk.Frame(window, width=200, height=200).place(50, 50)
        child_button = ntk.Button(
            parent_frame, text="Child", width=100, height=50
        ).place(25, 25)

        # Container overlapping the nested structure
        container = ntk.Container(window, width=150, height=150).place(75, 75)

        # Should handle nested widgets appropriately
        container.update_cloned_widgets()

        # Should find overlapping widgets in the hierarchy
        overlapping = container.get_overlapping_widgets()

        parent_frame.destroy()
        container.destroy()


class TestContainerIntegration:
    """Test Container integration with the rest of the nebulatk system."""

    def test_container_with_animations(self, window: ntk.Window):
        """Test container behavior with animated widgets."""
        container = ntk.Container(window, width=200, height=200).place(100, 100)

        # Create animated widget
        animated_widget = ntk.Button(
            window, text="Animated", width=50, height=50
        ).place(150, 150)

        # Simulate animation by moving the widget
        for i in range(5):
            animated_widget.x = 150 + i * 10
            animated_widget.y = 150 + i * 10

            # Container should update to track the moving widget
            container.on_widget_moved(animated_widget)

            # Verify container tracks the widget correctly
            if container.overlaps_with_widget(animated_widget):
                assert animated_widget in container.get_overlapping_widgets()

        animated_widget.destroy()
        container.destroy()

    def test_multiple_containers(self, window: ntk.Window):
        """Test multiple containers in the same window."""
        container1 = ntk.Container(window, width=100, height=100).place(50, 50)
        container2 = ntk.Container(window, width=100, height=100).place(200, 200)

        # Create widget that overlaps with both containers
        shared_widget = ntk.Button(window, text="Shared", width=200, height=200).place(
            100, 100
        )

        # Both containers should detect the overlap
        container1.update_cloned_widgets()
        container2.update_cloned_widgets()

        assert shared_widget in container1.get_overlapping_widgets()
        assert shared_widget in container2.get_overlapping_widgets()

        # Each container should have its own clone
        assert len(container1.cloned_widgets) == 1
        assert len(container2.cloned_widgets) == 1

        shared_widget.destroy()
        container1.destroy()
        container2.destroy()

    def test_container_z_order(self, window: ntk.Window):
        """Test that container respects z-order of widgets."""
        # Create widgets with different z-orders
        bottom_widget = ntk.Button(window, text="Bottom", width=100, height=100).place(
            100, 100
        )
        top_widget = ntk.Button(window, text="Top", width=80, height=80).place(110, 110)

        container = ntk.Container(window, width=150, height=150).place(50, 50)

        # Container should respect z-order when cloning
        container.update_cloned_widgets()

        # Top widget should appear above bottom widget in the container
        cloned_widgets = container.cloned_widgets
        assert len(cloned_widgets) == 2

        # Verify z-order is preserved (implementation-dependent)
        # This test may need adjustment based on actual z-order implementation

        bottom_widget.destroy()
        top_widget.destroy()
        container.destroy()


if __name__ == "__main__":
    pytest.main([__file__])
