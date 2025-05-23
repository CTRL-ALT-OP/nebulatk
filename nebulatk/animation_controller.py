from time import sleep

from typing import Callable

import threading
import warnings

from collections.abc import Iterable

try:
    import colors_manager
    import standard_methods
except ImportError:
    from . import colors_manager
    from . import standard_methods


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


class Animation:
    """A class to handle widget animations for multiple attributes with different easing curves."""

    def __init__(
        self,
        widget: object,
        target_attributes: dict[str, float | str],
        duration: float = 0.5,
        steps: int = 60,
        curve: Callable[[float], float] = Curves.linear,
        looping: bool = False,
        threadless: bool = False,
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
        self.threadless = threadless
        self.widget = widget
        self.thread = None
        self.duration = duration
        self.current_values = {}
        self.target_values = {}
        self.update_current_values(target_attributes)
        self.running = False
        self.manually_stopped = False
        self.curve = curve
        self.steps = steps
        self.step = 0
        self.looping = looping

    def update_current_values(self, target_attributes: dict[str, float | str]):

        if not isinstance(target_attributes, dict):
            warnings.warn(
                "target_attributes must be a dictionary, skipping...",
                category=Warning,
                stacklevel=2,
            )
            return
        for attr, target_val in target_attributes.items():
            if not hasattr(self.widget, attr):
                warnings.warn(
                    f"Widget does not have attribute: {attr}, skipping...",
                    category=Warning,
                    stacklevel=2,
                )
                continue
            current_val = getattr(self.widget, attr)
            # Check if this is a color attribute
            if isinstance(
                target_val, (colors_manager.Color, str, list, tuple)
            ):  # Hex or Color object
                try:
                    # Convert current and target to RGB
                    current_rgb = colors_manager.convert_to_rgb(current_val)
                    if isinstance(target_val, colors_manager.Color):
                        target_rgb = colors_manager.convert_to_rgb(target_val.color)
                    else:
                        target_rgb = colors_manager.convert_to_rgb(
                            colors_manager.Color(target_val).color
                        )

                    if target_rgb is None:
                        warnings.warn(
                            f"Invalid color for {attr}: {target_rgb}, skipping...",
                            category=Warning,
                            stacklevel=2,
                        )
                        continue
                    self.current_values[attr] = current_rgb  # [r, g, b, a]
                    self.target_values[attr] = target_rgb  # [r, g, b, a]
                except Exception as e:
                    warnings.warn(
                        f"Invalid color for {attr}: {target_val}, {e}, skipping...",
                        category=Warning,
                        stacklevel=2,
                    )
            elif isinstance(current_val, (int, float)) and isinstance(
                target_val, (int, float)
            ):
                self.current_values[attr] = float(current_val)
                self.target_values[attr] = float(target_val)
            else:
                warnings.warn(
                    f"Attribute {attr} is not numeric or a valid color, skipping...",
                    category=Warning,
                    stacklevel=2,
                )
                continue

    def start(self) -> None:
        """Animate the widget to target coordinates with specified easing curve.

        Args:
        """
        self.update_current_values(self.target_values)
        self.widget.master.active_animations.append(self)
        self.start_values = self.current_values.copy()
        self.running = True
        if not self.threadless:
            self.thread = threading.Thread(target=self.run)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            # Set a flag to indicate that the animation was stopped manually
            self.manually_stopped = True
        if self in self.widget.master.active_animations:
            self.widget.master.active_animations.remove(self)

    def join(self, timeout):
        if self.thread:
            return self.thread.join(timeout)

    def tick(self, direction: int = 1):
        t = self.step / (self.steps * self.duration)
        eased_t = self.curve(t)

        # Update all attributes
        updated_values = {}
        for attr in self.target_values:
            if isinstance(self.target_values[attr], (list, tuple)):
                # Interpolate RGB components
                updated_values[attr] = [
                    standard_methods.clamp(
                        int(
                            self.start_values[attr][i]
                            + (self.target_values[attr][i] - self.start_values[attr][i])
                            * eased_t
                        ),
                        0,
                        255,
                    )
                    for i in range(len(self.start_values[attr]))
                ]

            else:
                # Existing numeric interpolation
                start_val = self.start_values[attr]
                target_val = self.target_values[attr]
                updated_values[attr] = start_val + (target_val - start_val) * eased_t

        # Apply final values at the last step
        if self.step == int(self.steps * self.duration):
            updated_values = self.target_values.copy()

        # Track which attributes need visual updates
        needs_position_update = False
        needs_size_update = False

        if "x" in updated_values or "y" in updated_values:
            needs_position_update = True

        if "width" in updated_values or "height" in updated_values:
            needs_size_update = True

        # Update widget attributes
        for attr, value in updated_values.items():
            setattr(self.widget, attr, value)

        # Force a visual update if needed
        if needs_position_update or needs_size_update:
            new_x = self.widget.x
            new_y = self.widget.y

            # Force an update by calling place which will update the visual representation
            self.widget.place(new_x, new_y)

        self.current_values = updated_values
        self.widget.update()
        self.step += direction

    def run(self) -> None:
        """
        Run the animation loop, updating all specified attributes.
        """
        # Initialize the manually_stopped flag
        self.manually_stopped = False

        if self.looping:
            while self.running:
                for _ in range(int(self.steps * self.duration)):
                    if not self.running:
                        break
                    self.tick()
                    sleep(1 / self.steps)
                for _ in range(int(self.steps * self.duration)):
                    if not self.running:
                        break
                    self.tick(-1)
                    sleep(1 / self.steps)
        else:
            for _ in range(int(self.steps * self.duration)):
                if not self.running:
                    break
                self.tick()
                sleep(1 / self.steps)

            # Only apply final values if the animation wasn't manually stopped
            if not self.manually_stopped:
                # Ensure final values are set directly at the end
                for attr, value in self.target_values.items():
                    # Handle special attributes like x and y that need special handling
                    if attr == "x":
                        self.widget._position[0] = value
                    elif attr == "y":
                        self.widget._position[1] = value
                    else:
                        setattr(self.widget, attr, value)

                # Force a final visual update
                if "x" in self.target_values or "y" in self.target_values:
                    self.widget.place(self.widget.x, self.widget.y)
                else:
                    self.widget.update()

            self.stop()


class AnimationGroup(threading.Thread):
    """A class to manage a sequence of animations with different curves and keyframes."""

    def __init__(
        self,
        widget: object,
        keyframes: (
            list[
                tuple[
                    float,
                    dict[str, float],
                    Callable[[float], float] | None,
                    float | None,
                ]
            ]
            | list[tuple[Animation, float | None]]
            | Animation
        ),
        steps: int = 60,
        looping: bool = False,
    ) -> None:
        """
        Initialize an animation group with keyframes.

        Args:
            widget: The widget to animate
            keyframes: List of tuples or existing Animation instances (duration, target_attributes, curve) or (Animation, trigger_time)
                       - duration: Time in seconds for this segment
                       - target_attributes: Dictionary of attribute names and target values
                       - curve: Easing function for this segment (defaults to linear)
                       - start_time: Time in seconds to start the animation (defaults to after the previous animation)
            steps: Steps per second for each animation (default 60)
        """
        super().__init__()
        self.widget = widget
        self.keyframes = []
        self.steps = steps
        self.running = False
        self.looping = looping
        self.thread = self

        for keyframe in keyframes:
            if not isinstance(keyframe, (Iterable, Animation)):
                warnings.warn(
                    f"Invalid keyframe format, keyframe must be an iterable or an Animation instance. Skipping: {keyframe}",
                    category=Warning,
                    stacklevel=2,
                )
                continue
            if isinstance(keyframe, Iterable):
                if len(keyframe) < 2:
                    warnings.warn(
                        f"Invalid keyframe format, keyframe must be an iterable with at least 2 elements. Skipping: {keyframe}",
                        category=Warning,
                        stacklevel=2,
                    )
                    continue
                if len(keyframe) > 4:
                    warnings.warn(
                        f"Invalid keyframe format, keyframe must be an iterable with at most 4 elements. Skipping last {len(keyframe) - 4} elements: {keyframe}",
                        category=Warning,
                        stacklevel=2,
                    )
            self.keyframes.append(keyframe)
        self.animations = self._build_animations()

    def _build_animations(self) -> list[Animation]:
        """Convert keyframes into a sequence of Animation instances."""
        animations = []

        current_time = 0
        end_time = 0
        for keyframe in self.keyframes:
            # Handle existing Animation instances
            if isinstance(keyframe, Animation):
                keyframe.steps = self.steps
                keyframe.threadless = True
                animations.append([keyframe, current_time])
                current_time += keyframe.duration
                end_time = max(end_time, current_time)
            # Handle existing Animation instances with start_times
            elif isinstance(keyframe[0], Animation):
                anim = keyframe[0]
                start_time = current_time if keyframe[1] is None else keyframe[1]
                animations.append([anim, start_time])
                anim.steps = self.steps
                anim.threadless = True
                current_time += start_time
                current_time += anim.duration
                end_time = max(end_time, start_time + anim.duration)
            elif isinstance(keyframe, Iterable):
                # Standardize keyframe format
                keyframe = [
                    keyframe[0],
                    keyframe[1],
                    Curves.linear if len(keyframe) < 3 else keyframe[2],
                    current_time if len(keyframe) < 4 else keyframe[3],
                ]
                duration, target_attrs, curve, start_time = keyframe
                anim = Animation(
                    widget=self.widget,
                    target_attributes=target_attrs,
                    duration=duration,
                    steps=self.steps,
                    curve=curve,
                    threadless=True,
                )
                animations.append([anim, start_time])
                current_time += duration

                end_time = max(end_time, current_time)

        self.length = end_time
        return animations

    def start(self) -> None:
        """Start the animation group."""
        self.running = True
        super().start()
        self.widget.master.active_animations.append(self)

    def stop(self) -> None:
        """Stop the animation group."""
        if self.running:
            self.running = False
            for anim in self.animations:
                anim[0].stop()
        self.widget.master.active_animations.remove(self)

    def run(self) -> None:
        """Run all animations in sequence."""

        def run_animation_sequence(direction: int = 1) -> None:
            """Helper function to run animation sequence in forward or reverse direction."""
            end = int(self.length * self.steps) + 1
            step_range = range(end) if direction == 1 else range(end, 0, -1)
            for step in step_range:
                if not self.running:
                    break
                for animation, start_time in self.animations:
                    step_start = start_time * self.steps
                    step_end = (start_time + animation.duration) * self.steps
                    if step_start <= step <= step_end:
                        if not animation.running:
                            animation.start()
                        animation.tick(direction)
                sleep(1 / self.steps)

        if not self.looping:
            run_animation_sequence()  # Single forward pass

        while self.looping and self.running:
            run_animation_sequence(1)  # Forward pass
            run_animation_sequence(-1)  # Reverse pass

        if self.running:
            for anim, _ in self.animations:
                anim.stop()
