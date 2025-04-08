from time import sleep

from typing import Callable

import threading
import warnings


class Curves:
    """
    A class for animating widget movements with different easing curves.

    This class provides various animation curves for moving widgets from one position
    to another with smooth transitions.
    """

    @staticmethod
    def linear(t: float) -> float:
        """
        Linear easing function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using linear easing
        """
        return t

    @staticmethod
    def ease_in_quad(t: float) -> float:
        """
        Quadratic ease-in function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using quadratic ease-in
        """
        return t**2

    @staticmethod
    def ease_out_quad(t: float) -> float:
        """
        Quadratic ease-out function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using quadratic ease-out
        """
        return t * (2 - t)

    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """
        Quadratic ease-in-out function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using quadratic ease-in-out
        """
        return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """
        Cubic ease-in function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using cubic ease-in
        """
        return t * t * t

    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """
        Cubic ease-out function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using cubic ease-out
        """
        return (t - 1) * (t - 1) * (t - 1) + 1

    @staticmethod
    def bounce(t: float) -> float:
        """
        Bounce easing function.

        Args:
            t: A value between 0 and 1 representing animation progress

        Returns:
            The interpolated value using bounce easing
        """
        if t < (1 / 2.75):
            return 7.5625 * t * t
        elif t < (2 / 2.75):
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < (2.5 / 2.75):
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375


class Animation(threading.Thread):
    """A class to handle widget animations for multiple attributes with different easing curves."""

    def __init__(
        self,
        widget: object,
        target_attributes: dict[str, float],
        duration: float = 0.5,
        steps: int = 60,
        curve: Callable[[float], float] = Curves.linear,
    ) -> None:
        """
        Initialize the animation controller for multiple attributes.

        Args:
            widget: The widget to animate
            target_attributes: Dictionary of attribute names and their target values
            duration: Duration of the animation in seconds
            steps: How many steps to take per second (60 is equivalent to 60fps)
            curve: Easing function to use (defaults to linear)
        """
        super().__init__()
        self.widget = widget
        self.duration = duration
        # Initialize current positions for all attributes
        self.current_values = {}
        self.target_values = {}

        for attr in target_attributes:
            if not hasattr(widget, attr):
                warnings.warn(
                    f"Widget does not have attribute: {attr}, skipping...",
                    category=Warning,
                    stacklevel=2,
                )
                continue
            if not isinstance(getattr(widget, attr), (int, float)):
                warnings.warn(
                    f"Attribute {attr} is not numeric, skipping...",
                    category=Warning,
                    stacklevel=2,
                )
                continue
            if not isinstance(target_attributes[attr], (int, float)):
                warnings.warn(
                    f"Target attribute {attr} is not numeric, skipping...",
                    category=Warning,
                    stacklevel=2,
                )
                continue
            self.current_values[attr] = float(getattr(widget, attr))
            self.target_values[attr] = float(target_attributes[attr])

        self.running = False
        self.curve = curve
        self.steps = steps
        self.start_values = self.current_values.copy()

    def start(self) -> None:
        """Animate the widget to target coordinates with specified easing curve.

        Args:
        """
        self.running = True
        super().start()

    def stop(self):
        if self.running:
            self.running = False

    def run(self) -> None:
        """
        Run the animation loop, updating all specified attributes.
        """
        for step in range(int(self.steps * self.duration) + 1):
            if not self.running:
                break
            t = step / (self.steps * self.duration)
            eased_t = self.curve(t)

            # Update all attributes
            updated_values = {}
            for attr in self.target_values:
                start_val = self.start_values[attr]
                target_val = self.target_values[attr]
                updated_values[attr] = start_val + (target_val - start_val) * eased_t

            # Apply final values at the last step
            if step == int(self.steps * self.duration):
                updated_values = self.target_values

            # Update widget attributes
            for attr, value in updated_values.items():
                setattr(self.widget, attr, value)

            self.current_values = updated_values
            self.widget.update()
            sleep(1 / self.steps)
