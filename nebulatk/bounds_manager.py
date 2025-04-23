try:
    from . import standard_methods
except ImportError:
    import standard_methods

from PIL import Image


def generate_bounds_for_nonstandard_image(image, tolerance=0.75):
    """Generates bounds for an image with arbitrary shapes and transparency

    Args:
        image (PilImage): Image to generate bounds for
        tolerance (float, optional): Minimum opacity required to be added to bounds. Defaults to 0.75.

    Returns:
        dict: Resultant bounds
    """
    if not isinstance(image, Image.Image):
        raise TypeError("Input image must be a PIL Image object.")

    width, height = image.size

    threshold = round(tolerance * 255)
    bounds = {}
    while not bounds and threshold >= 0:
        # Optimized pixel access using getdata()
        pixels = list(image.getdata())
        for y in range(height):
            row_bounds = []
            start_pixel = None

            row_pixels = pixels[y * width : (y + 1) * width]
            for x, pixel in enumerate(row_pixels):
                if isinstance(pixel, int):  # Handle single-channel images
                    opacity = pixel
                else:
                    opacity = (
                        pixel[3] if len(pixel) > 3 else 255
                    )  # Default to opaque if no alpha channel

                if opacity >= threshold:
                    if start_pixel is None:
                        start_pixel = x
                elif start_pixel is not None:
                    row_bounds.append([start_pixel, x - 1])
                    start_pixel = None

            if start_pixel is not None:
                row_bounds.append([start_pixel, width - 1])

            if row_bounds:
                bounds[y] = row_bounds
        # In case no bounds were found, reduce tolerance
        threshold -= 10

    return bounds


def check_hit(_object, x, y):
    """Checks if a point is inside a given object's rectangular bounds approximation"""
    if not _object.initialized:
        return False
    if not _object.visible:
        return False

    if not _object.can_focus:
        return False

    hit = (int(x), int(y))
    a, b, c, d = standard_methods.get_rect_points(_object)

    rect_area = standard_methods.get_rect_area(_object)

    area_apd = standard_methods.get_triangle_area(a, hit, d)
    area_dpc = standard_methods.get_triangle_area(d, hit, c)
    area_cpb = standard_methods.get_triangle_area(c, hit, b)
    area_pba = standard_methods.get_triangle_area(hit, b, a)

    # If the sum of the areas of the triangles apd, dpc, cpb, and pba are less than or equal to the rectangle area, we are inside it.
    # Generally on a hit, the sum of the area of the triangles should always be equal to the area of the triangles
    if sum((area_apd, area_dpc, area_cpb, area_pba)) <= rect_area:
        if _object.bounds_type != "non-standard":
            return True
        x, y = standard_methods.get_rel_point_rect(_object, x, y)
        if y not in _object.bounds:
            return False

        for bounds in _object.bounds[y]:
            if bounds[0] <= x and bounds[1] >= x:
                return True
    return False


def __OLD_remove_bounds(item, old_x, old_y, mode="box"):
    """Remove the bounds of a widget

    Args:
        item (nebulatk.Widget): widget
        mode (str, optional): Mode to remove bounds with. Defaults to "box".
    """

    x, y = standard_methods.rel_position_to_abs(item, old_x, old_y)

    if mode == "box":
        for i in range(y, y + item.height):
            if i in item.master.bounds:
                for j in range(len(item.master.bounds[i])):
                    if item.master.bounds[i][j][0] == item:
                        item.master.bounds[i].pop(j)
                        break

    elif mode == "non-standard":
        for i in item.bounds.keys():
            for bound in item.bounds[i]:
                if i in item.master.bounds:
                    for j in range(len(item.master.bounds[i])):
                        if (
                            item.master.bounds[i][j][0] == item
                            and item.master.bounds[i][j][1] == bound[0] + x
                        ):
                            item.master.bounds[i].pop(j)
                            break


def __OLD_update_bounds(item, old_x, old_y, x, y, mode="box"):
    """Update the bounds of a widget

    Args:
        item (nebulatk.Widget): widget
        x (int): x
        y (int): y
        mode (str, optional): Mode to update bounds with. Defaults to "box".
    """

    # Set x and y in case none is provided
    if x is None:
        x = item.x
    if y is None:
        y = item.y

    x, y = standard_methods.rel_position_to_abs(item, x, y)
    # Remove old bounds
    __OLD_remove_bounds(item, old_x, old_y, mode)
    if mode == "box":
        # Add in new bounds
        for i in range(y, y + item.height):
            if i in item.master.bounds:
                if item.master.bounds[i] != []:
                    for j in range(len(item.master.bounds[i])):
                        if item.master.bounds[i][j][0].object < item.object:
                            item.master.bounds[i].insert(j, [item, x, x + item.width])
                            break
                else:
                    item.master.bounds[i] = [[item, x, x + item.width]]
            else:
                item.master.bounds[i] = [[item, x, x + item.width]]

    elif mode == "non-standard":
        # Add in new bounds
        # Iterate over all y values in the new bounds
        for i in item.bounds.keys():

            # Iterate over all lines defined in the new bounds[y]
            for bound in item.bounds[i]:

                # If there is already a list of objects in the master bounds at this y
                if i + y in item.master.bounds:

                    # Check if the list of objects is empty
                    if item.master.bounds[i] != []:

                        # If it isn't empty, iterate over all existing objects in the master bounds until we find an object that the bounds should be behind
                        for j in range(len(item.master.bounds[i + y])):
                            if item.master.bounds[i + y][j][0].object < item.object:
                                item.master.bounds[i + y].insert(
                                    j, [item, bound[0] + x, bound[1] + x]
                                )

                                # Stop looking
                                break

                    # Otherwise, create new list of objects in master bounds
                    else:
                        item.master.bounds[i] = [[item, bound[0] + x, bound[1] + x]]
                else:
                    item.master.bounds[i] = [[item, bound[0] + x, bound[1] + x]]
