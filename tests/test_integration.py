import sys
import os
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../nebulatk"))
)

# Import nebulatk
import nebulatk as ntk
import animation_controller


class TestIntegration:
    """Integration tests for nebulatk components working together."""

    @pytest.fixture
    def app(self):
        """Create a test application window."""
        window = ntk.Window(title="Integration Test", width=800, height=600)
        yield window
        window.close()

    def test_component_hierarchy(self, app):
        """Test component parent-child relationships."""
        # Create a panel to hold other widgets
        panel = ntk.Frame(app, width=400, height=300, fill="sgilightgray").place(
            x=50, y=50
        )

        # Add widgets to the panel
        button = ntk.Button(panel, text="Submit", width=100, height=30).place(
            x=20, y=20
        )
        label = ntk.Label(panel, text="Hello World", width=200, height=30).place(
            x=20, y=70
        )

        # Check parent-child relationships
        assert panel in app.children
        assert button in panel.children
        assert label in panel.children

        # Check that widgets inherit properties from parent
        assert button.root == panel
        assert label.root == panel
        assert panel.root == app

        # Test destruction of parent destroys children
        panel.destroy()
        assert panel not in app.children
        assert not hasattr(button, "_tk_widget")  # Button should be destroyed
        assert not hasattr(label, "_tk_widget")  # Label should be destroyed

    def test_event_binding(self, app):
        """Test event binding across widgets."""
        # Create a button with a click handler
        clicked = [False]  # Use list to modify from closure

        def on_click():
            clicked[0] = True

        button = ntk.Button(
            app, text="Click Me", width=100, height=30, command=on_click
        ).place(x=50, y=50)

        # Simulate button click
        button.clicked()  # Call private method to simulate click

        assert clicked[0]  # Click handler should have been called

    def test_widget_state_changes(self, app):
        """Test state changes and visual feedback."""
        # Create widgets with different states
        button = ntk.Button(app, text="Enabled", mode="toggle").place(x=50, y=50)

        button.clicked()  # Call private method to simulate click
        # Test disabling a button
        assert button.state

    def test_animation_integration(self, app):
        """Test animation integration with widgets."""
        # Create a button to animate
        button = ntk.Button(app, text="Animate Me", width=100, height=30).place(
            x=50, y=50
        )

        # Create animation
        animation = animation_controller.Animation(
            widget=button,
            target_attributes={"x": 100, "y": 50},
            duration=0.1,
            steps=10,
        )
        animation.start()
        animation.join()

        # Button should have moved
        assert button.x == 100
        assert button.y == 50

    def test_widget_styling(self, app):
        """Test consistent styling across widgets."""
        # Create a set of widgets with common styling
        common_style = {
            "fill": "blue",
            "text_color": "white",
            "width": 150,
            "height": 40,
        }

        button = ntk.Button(app, text="Styled Button", **common_style).place(x=50, y=50)
        label = ntk.Label(app, text="Styled Label", **common_style).place(x=50, y=100)

        # Verify consistent styling
        assert button.fill == "#0000FF"
        assert label.fill == "#0000FF"

        assert button.text_color == "#FFFFFF"
        assert label.text_color == "#FFFFFF"

    def test_layout_management(self, app):
        """Test layout management and positioning."""
        # Create a container with child widgets
        container = ntk.Frame(app, width=400, height=300).place(x=50, y=50)

        # Create widgets with different positioning strategies
        button1 = ntk.Button(container, text="Button 1", width=100, height=30).place(
            x=20, y=20
        )
        button2 = ntk.Button(container, text="Button 2", width=100, height=30).place(
            x=20, y=70
        )
        button3 = ntk.Button(container, text="Button 3", width=100, height=30).place(
            x=150, y=20
        )

        # Check absolute positioning
        assert button1.x == 20
        assert button1.y == 20
        assert button2.y > button1.y
        assert button3.x > button1.x

        # Move the container and check that children maintain relative positions
        container.place(x=100, y=100)
        container.update()

        # The relative positions should be maintained
        assert button1.x == 20  # Relative x position stays the same
        assert button1.y == 20  # Relative y position stays the same
