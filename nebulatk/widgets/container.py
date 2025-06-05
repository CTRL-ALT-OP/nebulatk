from .base import Component
from tkinter import Canvas
import tkinter as tk

# Import modules needed for widget management
try:
    from .. import bounds_manager, defaults
except ImportError:
    import bounds_manager, defaults


class Container(Component):

    def __init__(
        self, root, width, height, fill=None, border=None, border_width=0, **kwargs
    ):
        self.initialized = False
        super().__init__(width, height)

        # Set up proper parent-child relationships for nebulatk widget hierarchy
        # The Container should be a child of the provided root, but act as a parent for its children
        self._root = root  # The Container's parent (usually the main window)
        self._window = (
            root if root.master == root else root.master
        )  # Reference to the top-level window

        # IMPORTANT: For containers, master should point to itself so that child widgets
        # draw on the container's canvas instead of the main window's canvas
        self.master = self

        # Container position (will be set when placed)
        self._container_x = 0
        self._container_y = 0

        # Add essential widget properties that the bounds manager and other systems expect
        self._orientation = 0  # Default orientation
        self.bounds_type = "default"  # Bounds type for hit detection
        self.state = False  # Whether the container is in an active state
        self.hovering = False  # Whether the container is being hovered
        self.visible = True
        self.can_focus = (
            True  # Allow container to receive focus so it can handle events
        )
        self.can_hover = True
        self.can_click = True

        # Add this container to its parent's children list
        self._root.children.append(self)

        # Initialize container-specific properties for managing child widgets
        self.children = []  # List to hold child widgets
        self.bounds = {}  # Bounds management for child widgets
        self.active = None  # Currently active (focused) widget
        self.down = None  # Widget currently being clicked
        self.hovered_child = None  # Child widget currently being hovered
        self.updates_all = (
            False  # Whether updates to members update the widget automatically
        )
        self.defaults = self._window.defaults  # Inherit defaults from window

        # Maps for canvas object replication
        self.maps = {}

        # Get the actual tkinter root window for creating the canvas
        # For nested containers, we need to traverse up to find the tkinter root
        current = self._window
        while hasattr(current, "_window") and current._window != current:
            current = current._window
        tkinter_root = current.root

        self.canvas = Canvas(tkinter_root, width=width, height=height)

        # Replicate existing canvas items from window
        for child in self._window.canvas.find_all():
            self.replicate_object(child)

        # Bind event handlers to the container's canvas
        self._bind_events()

        # Ensure proper layering after initialization
        self._ensure_proper_layering()

        self.initialized = True

    # Container acts as both a widget (has a root) and a parent (for its children)
    @property
    def root(self):
        """Return the Container's parent (what it's contained in)"""
        return self._root

    @root.setter
    def root(self, root):
        """Set the Container's parent"""
        if self._root is not None:
            self._root.children.remove(self)
        self._root = root
        self._window = root if root.master == root else root.master
        if root is not None:
            root.children.append(self)

    # Add the x and y properties that widgets expect from their parent
    @property
    def x(self):
        return self._container_x

    @x.setter
    def x(self, x):
        self._container_x = x

    @property
    def y(self):
        return self._container_y

    @y.setter
    def y(self, y):
        self._container_y = y

    # Add orientation property that bounds manager expects
    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation

    # Add window property for accessing the original window_internal object
    # This is needed for image creation and other operations that need the top-level window
    @property
    def window(self):
        """Access the original window_internal object"""
        return self._window

    def _bind_events(self):
        """Bind event handlers for mouse and keyboard events"""
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<ButtonRelease-1>", self.click_up)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", self.leave_container)
        self.canvas.bind("<KeyPress>", self.typing)
        self.canvas.bind("<KeyRelease>", self.typing_up)
        self.canvas.focus_set()  # Allow canvas to receive keyboard events

    def click(self, event):
        """Handle mouse click events - similar to main window's click handler"""
        # Convert canvas coordinates to container-relative coordinates
        x = int(event.x)
        y = int(event.y)

        # Find the child widget that was clicked
        active_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )

        # Update active widget
        if active_new is not self.active:
            if self.active is not None:
                self.active.change_active()
            self.active = active_new

        # Handle click down
        if active_new is not self.down:
            self.down = active_new
            if active_new is not None:
                active_new.clicked(x, y)

    def click_up(self, event):
        """Handle mouse click release events"""
        if self.down:
            self.down.release()
            self.down = None

    def hover(self, event):
        """Handle mouse hover events"""
        x = int(event.x)
        y = int(event.y)

        # Handle dragging if something is being clicked
        if self.down is not None:
            self.down.dragging(x, y)

        # Find hovered widget
        hovered_new = next(
            (child for child in self.children if bounds_manager.check_hit(child, x, y)),
            None,
        )

        # Update hovered widget
        if hovered_new is not self.hovered_child:
            if self.hovered_child is not None:
                self.hovered_child.hover_end()
            self.hovered_child = hovered_new
            if hovered_new is not None:
                hovered_new.hovered()

    def leave_container(self, event):
        """Handle mouse leaving container"""
        if self.hovered_child is not None:
            self.hovered_child.hover_end()
            self.hovered_child = None

    def typing(self, event):
        """Handle key press events"""
        if self.active is not None and self.active.can_type:
            self.active.typed(event.char)

    def typing_up(self, event):
        """Handle key release events"""
        # Can be extended for specific key release handling
        pass

    # Canvas drawing methods - delegate to container's canvas
    def create_image(self, x, y, image, state="normal"):
        """Create image on container's canvas"""
        # Get the tkinter-compatible image
        if hasattr(image, "tk_image"):
            # This is an image_manager.Image object
            tk_image = image.tk_image(self)
        else:
            # This is already a tkinter-compatible image
            tk_image = image

        image_id = self.canvas.create_image(
            x, y, image=tk_image, state=state, tags=("fg_item",)
        )
        return (image_id, image)

    def create_rectangle(
        self,
        x,
        y,
        width,
        height=0,
        fill=0,
        border_width=0,
        outline=None,
        state="normal",
    ):
        """Create rectangle on container's canvas"""
        if x == width or y == height:
            return None, None

        # Import image_manager here to avoid circular imports
        try:
            from .. import image_manager
        except ImportError:
            import image_manager

        # To support transparency with RGBA, check if the rectangle includes transparency
        if fill is not None and len(str(fill)) > 7 and str(fill)[7:] != "ff":
            bg_image = image_manager.create_image(
                fill, int(width - x), int(height - y), outline, border_width, self
            )
            id, image = self.create_image(x, y, bg_image, state=state)
            return id, image

        # Otherwise create a regular rectangle
        rect = self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill=fill[:7] if fill is not None else fill,
            outline=outline[:7] if outline is not None else outline,
            width=border_width,
            state=state,
            tags=("fg_item",),
        )
        return (rect, None)

    def create_text(
        self, x, y, text, font, fill="black", anchor="center", state="normal", angle=0
    ):
        """Create text on container's canvas"""
        text_id = self.canvas.create_text(
            x,
            y,
            text=text,
            font=font,
            fill=fill,
            anchor=anchor,
            state=state,
            angle=angle,
            tags=("fg_item",),
        )
        return (text_id, None)

    def move(self, _object, x, y):
        """Move object on container's canvas"""
        self.canvas.coords(_object, x, y)

    def object_place(self, _object, x, y):
        """Place object on container's canvas"""
        self.canvas.coords(_object, x, y)

    def delete(self, _object):
        """Delete object from container's canvas"""
        self.canvas.delete(_object)

    def change_state(self, _object, state):
        """Change state of object on container's canvas"""
        self.canvas.itemconfig(_object, state=state)

    def configure(self, _object=None, **kwargs):
        """Configure object on container's canvas"""
        if _object is not None:
            self.canvas.itemconfig(_object, **kwargs)

    def replicate_object(self, child):
        # Check if the object exists on the window canvas
        try:
            # Verify the object exists by checking if it's in the list of all items
            if child not in self._window.canvas.find_all():
                return  # Object doesn't exist, skip replication

            item_type = self._window.canvas.type(child)
            coords = self._window.canvas.coords(child)
            adjusted_coords = []
            for i, coord in enumerate(coords):
                if i % 2 == 0:  # x coordinates (even indices)
                    adjusted_coords.append(coord - self._container_x)
                else:  # y coordinates (odd indices)
                    adjusted_coords.append(coord - self._container_y)

            coords = adjusted_coords
        except tk.TclError:
            # Object doesn't exist or is invalid, skip replication
            return

        # During initialization, we replicate with original coordinates
        # Position adjustment will happen later in place() method
        if item_type == "image":
            self.maps[child] = self.canvas.create_image(
                coords[0],
                coords[1],
                image=self._window.canvas.itemcget(child, "image"),
                anchor=self._window.canvas.itemcget(child, "anchor"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "rectangle":
            self.maps[child] = self.canvas.create_rectangle(
                coords[0],
                coords[1],
                coords[2],
                coords[3],
                fill=self._window.canvas.itemcget(child, "fill"),
                outline=self._window.canvas.itemcget(child, "outline"),
                width=self._window.canvas.itemcget(child, "width"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "text":
            self.maps[child] = self.canvas.create_text(
                coords[0],
                coords[1],
                text=self._window.canvas.itemcget(child, "text"),
                font=self._window.canvas.itemcget(child, "font"),
                fill=self._window.canvas.itemcget(child, "fill"),
                anchor=self._window.canvas.itemcget(child, "anchor"),
                state=self._window.canvas.itemcget(child, "state"),
                angle=self._window.canvas.itemcget(child, "angle"),
                tags=("background_item",),
            )
        elif item_type == "line":
            self.maps[child] = self.canvas.create_line(
                *coords,
                fill=self._window.canvas.itemcget(child, "fill"),
                width=self._window.canvas.itemcget(child, "width"),
                stipple=self._window.canvas.itemcget(child, "stipple"),
                arrow=self._window.canvas.itemcget(child, "arrow"),
                arrowshape=self._window.canvas.itemcget(child, "arrowshape"),
                capstyle=self._window.canvas.itemcget(child, "capstyle"),
                joinstyle=self._window.canvas.itemcget(child, "joinstyle"),
                smooth=self._window.canvas.itemcget(child, "smooth"),
                splinesteps=self._window.canvas.itemcget(child, "splinesteps"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "oval":
            self.maps[child] = self.canvas.create_oval(
                coords[0],
                coords[1],
                coords[2],
                coords[3],
                fill=self._window.canvas.itemcget(child, "fill"),
                outline=self._window.canvas.itemcget(child, "outline"),
                width=self._window.canvas.itemcget(child, "width"),
                stipple=self._window.canvas.itemcget(child, "stipple"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "polygon":
            self.maps[child] = self.canvas.create_polygon(
                *coords,
                fill=self._window.canvas.itemcget(child, "fill"),
                outline=self._window.canvas.itemcget(child, "outline"),
                width=self._window.canvas.itemcget(child, "width"),
                stipple=self._window.canvas.itemcget(child, "stipple"),
                smooth=self._window.canvas.itemcget(child, "smooth"),
                splinesteps=self._window.canvas.itemcget(child, "splinesteps"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "arc":
            self.maps[child] = self.canvas.create_arc(
                coords[0],
                coords[1],
                coords[2],
                coords[3],
                fill=self._window.canvas.itemcget(child, "fill"),
                outline=self._window.canvas.itemcget(child, "outline"),
                width=self._window.canvas.itemcget(child, "width"),
                stipple=self._window.canvas.itemcget(child, "stipple"),
                start=self._window.canvas.itemcget(child, "start"),
                extent=self._window.canvas.itemcget(child, "extent"),
                style=self._window.canvas.itemcget(child, "style"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )
        elif item_type == "bitmap":
            self.maps[child] = self.canvas.create_bitmap(
                coords[0],
                coords[1],
                bitmap=self._window.canvas.itemcget(child, "bitmap"),
                anchor=self._window.canvas.itemcget(child, "anchor"),
                foreground=self._window.canvas.itemcget(child, "foreground"),
                background=self._window.canvas.itemcget(child, "background"),
                state=self._window.canvas.itemcget(child, "state"),
                tags=("background_item",),
            )

        # After replicating, ensure background items stay behind container widgets
        if self.canvas.find_withtag("fg_item"):
            self.canvas.tag_lower("background_item", "fg_item")
        else:
            self.canvas.tag_lower("background_item")

    def _show(self, root):
        pass

    def _hide(self, root):
        pass

    def place(self, x, y):
        """Place the container at specified position"""
        self._container_x = x
        self._container_y = y
        self.canvas.place(x=x, y=y)

        # Update positions of replicated background objects now that we know the container's position
        self._update_background_positions()

        return self

    def _update_background_positions(self):
        """Update the positions of replicated background objects relative to container position."""
        for original_item, replicated_item in self.maps.items():
            try:
                # Get original coordinates from the main window canvas
                if original_item not in self._window.canvas.find_all():
                    continue  # Original item no longer exists

                original_coords = self._window.canvas.coords(original_item)

                # Adjust coordinates relative to the container's position
                adjusted_coords = []
                for i, coord in enumerate(original_coords):
                    if i % 2 == 0:  # x coordinates (even indices)
                        adjusted_coords.append(coord - self._container_x)
                    else:  # y coordinates (odd indices)
                        adjusted_coords.append(coord - self._container_y)

                # Update the replicated object's position
                self.canvas.coords(replicated_item, *adjusted_coords)

            except tk.TclError:
                # Original item or replicated item no longer exists
                continue

    # Event handler methods that widgets are expected to have
    def hovered(self):
        """Handle hover events on the container"""
        self.hovering = True

    def hover_end(self):
        """Handle hover end events on the container"""
        self.hovering = False

    def clicked(self, x=None, y=None):
        """Handle click events on the container"""
        # Container can handle its own click logic here if needed
        pass

    def release(self):
        """Handle mouse release events on the container"""
        # Container can handle its own release logic here if needed
        pass

    def dragging(self, x, y):
        """Handle dragging events on the container"""
        # Container can handle its own dragging logic here if needed
        pass

    def change_active(self):
        """Handle active state changes"""
        # Container can handle its own active state changes here if needed
        pass

    def _ensure_proper_layering(self):
        """Ensure background items stay behind foreground items"""
        # Move all background items to the back
        if self.canvas.find_withtag("background_item"):
            self.canvas.tag_lower("background_item")
        # Move all foreground items to the front
        if self.canvas.find_withtag("fg_item"):
            self.canvas.tag_raise("fg_item")
