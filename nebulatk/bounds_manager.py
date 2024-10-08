try:
    from . import standard_methods
except ImportError:
    import standard_methods


def generate_bounds_for_nonstandard_image(image, tolerance=0.75):
    """Generates bounds for an image with arbitrary shapes and transparency

    Args:
        image (PilImage): Image to generate bounds for
        tolerance (float, optional): Minimum opacity required to be added to bounds. Defaults to 0.75.

    Returns:
        dict: Resultant bounds
    """
    pixels = image.load()
    width, height = image.size

    bounds = {}
    start_pixel = None

    # Execute function twice if no bounds are found the first pass
    while not bounds and tolerance >= 0:
        # Iterate over the pixels
        for y in range(height):
            for x in range(width):
                cpixel = pixels[x, y]

                # If the pixel is opaque enough to be over the tolerance threshold, and no line start was found, it is the start of a line
                if cpixel[3] >= round(tolerance * 255):
                    if start_pixel is None:
                        start_pixel = x

                # If the pixel doesn't hit the tolerance threshold, the line ends with the previous pixel
                elif start_pixel is not None:
                    # Add line to the bounds
                    if y in bounds:
                        bounds[y].append([start_pixel, x - 1])
                    else:
                        bounds[y] = [[start_pixel, x - 1]]
                    start_pixel = None

            # If no end to the line was found, the line must continue to the end
            if start_pixel is not None:
                bounds[y] = [[start_pixel, x]]
                start_pixel = None

        # In case no bounds were found, reduce tolerance
        tolerance -= tolerance
    return bounds


def remove_bounds(item, mode="box"):
    """Remove the bounds of a widget

    Args:
        item (nebulatk.Widget): widget
        mode (str, optional): Mode to remove bounds with. Defaults to "box".
    """

    x, y = standard_methods.rel_position_to_abs(item, item.x, item.y)

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


def update_bounds(item, x, y, mode="box"):
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
    remove_bounds(item, mode)
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
