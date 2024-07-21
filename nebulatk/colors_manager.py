import string


def convert_to_hex(color):
    """Convert arbitrary color type to a hex string

    Args:
        color (color): color

    Returns:
        str: Hex color string
    """
    # Load default color list
    global colors

    # If color is a string,
    if type(color) == str:
        # If doesn't start with '#', check if it's a hex string
        if not color.startswith("#"):
            # If it is a hex string, add '#' to the beginning and return it
            if all(c in string.hexdigits for c in color):
                return "#" + color

            # If it's not a hex string, it must be a default color
            # Return hex string from default color
            return colors[color][0]

        # If color is a hex string, return it
        return color

    # If color is a list, convert it to a tuple
    elif type(color) == list:
        color = tuple(color)

    # If color is a tuple, check if it is RGB or RGBA
    # Convert to hex and return result
    if type(color) == tuple:
        if len(color) > 3:
            return "#%02x%02x%02x%02x" % color
        return "#%02x%02x%02x" % color


def convert_to_rgb(color):
    """Convert arbitrary color type to a RGB or RGBA tuple

    Args:
        color (color): color

    Returns:
        tuple: RGB or RGBA color tuple
    """
    # Load default color list
    global colors

    # If color is a string,
    if type(color) == str:
        # If doesn't start with '#', check if it's a hex string. If it isn't, it must be a default color.
        if not color.startswith("#"):
            if not all(c in string.hexdigits for c in color):
                return colors[color][1]

        # Strip '#' off end
        color = color.lstrip("#")

        # If RGBA convert to hex string with 4 channels
        if len(color) > 6:
            return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4, 6))

        # Else convert to hex string with 3 channels
        return tuple(int(color[i : i + 2], 16) for i in (0, 2, 4))

    # If it is already a RGB or RGBA tuple, return the tuple version of it
    elif type(color) in (list, tuple):
        color = tuple(color)
        return color


def check_full_white_or_black(color):
    """Check if a color is (255,255,255) or (0,0,0). Supports RGBA colors

    Args:
        color (color): color

    Returns:
        int: Returns 1 if all white, -1 if all black, 0 if neither
    """
    # Convert color to RGB format
    color = convert_to_rgb(color)

    # Check sum of first 3 elements in color
    sum_all = sum(color[0:3])

    # All white
    if sum_all == 255 * 3:
        return 1

    # All black
    if sum_all == 0:
        return -1

    # Neither
    return 0


def brighten(color, increment=10):
    """Brighten a color by an increment.

    Args:
        color (color): color
        increment (int, optional): Increment to brighten color by. Out of 255. Defaults to 10.

    Returns:
        str: Hex color string
    """
    # Convert color to rgb
    color = convert_to_rgb(color)

    # If RGBA
    if len(color) > 3:
        return convert_to_hex(
            (
                # Clamp color values to 255 or lower
                min(color[0] + increment, 255),
                min(color[1] + increment, 255),
                min(color[2] + increment, 255),
                color[3],
            )
        )

    # If RGB
    return convert_to_hex(
        (
            # Clamp color values to 255 or lower
            min(color[0] + increment, 255),
            min(color[1] + increment, 255),
            min(color[2] + increment, 255),
        )
    )


def darken(color, increment=10):
    """Darken a color by an increment.

    Args:
        color (color): color
        increment (int, optional): Increment to darken color by. Out of 255. Defaults to 10.

    Returns:
        str: Hex color string
    """
    # Convert color to rgb
    color = convert_to_rgb(color)

    # If RGBA
    if len(color) > 3:
        return convert_to_hex(
            (
                # Clamp color values to 0 or higher
                max(color[0] - increment, 0),
                max(color[1] - increment, 0),
                max(color[2] - increment, 0),
                color[3],
            )
        )

    # If RGB
    return convert_to_hex(
        (
            # Clamp color values to 0 or higher
            max(color[0] - increment, 0),
            max(color[1] - increment, 0),
            max(color[2] - increment, 0),
        )
    )


global colors

# Color list loaded from TCL
colors = {
    "aliceblue": ["#F0F8FF", [240, 248, 255]],
    "antiquewhite": ["#FAEBD7", [250, 235, 215]],
    "antiquewhite1": ["#FFEFDB", [255, 239, 219]],
    "antiquewhite2": ["#EEDFCC", [238, 223, 204]],
    "antiquewhite3": ["#CDC0B0", [205, 192, 176]],
    "antiquewhite4": ["#8B8378", [139, 131, 120]],
    "aqua": ["#00FFFF", [0, 255, 255]],
    "aquamarine1": ["#7FFFD4", [127, 255, 212]],
    "aquamarine2": ["#76EEC6", [118, 238, 198]],
    "aquamarine3": ["#66CDAA", [102, 205, 170]],
    "aquamarine4": ["#458B74", [69, 139, 116]],
    "azure": ["#007FFF", [0, 127, 255]],
    "azure1": ["#F0FFFF", [240, 255, 255]],
    "azure2": ["#E0EEEE", [224, 238, 238]],
    "azure3": ["#C1CDCD", [193, 205, 205]],
    "azure4": ["#838B8B", [131, 139, 139]],
    "banana": ["#E3CF57", [227, 207, 87]],
    "beige": ["#F5F5DC", [245, 245, 220]],
    "bisque1": ["#FFE4C4", [255, 228, 196]],
    "bisque2": ["#EED5B7", [238, 213, 183]],
    "bisque3": ["#CDB79E", [205, 183, 158]],
    "bisque4": ["#8B7D6B", [139, 125, 107]],
    "black": ["#000000", [0, 0, 0]],
    "blanchedalmond": ["#FFEBCD", [255, 235, 205]],
    "blue": ["#0000FF", [0, 0, 255]],
    "blue2": ["#0000EE", [0, 0, 238]],
    "blue3": ["#0000CD", [0, 0, 205]],
    "blue4": ["#00008B", [0, 0, 139]],
    "blueviolet": ["#8A2BE2", [138, 43, 226]],
    "brick": ["#9C661F", [156, 102, 31]],
    "brown": ["#A52A2A", [165, 42, 42]],
    "brown1": ["#FF4040", [255, 64, 64]],
    "brown2": ["#EE3B3B", [238, 59, 59]],
    "brown3": ["#CD3333", [205, 51, 51]],
    "brown4": ["#8B2323", [139, 35, 35]],
    "burlywood": ["#DEB887", [222, 184, 135]],
    "burlywood1": ["#FFD39B", [255, 211, 155]],
    "burlywood2": ["#EEC591", [238, 197, 145]],
    "burlywood3": ["#CDAA7D", [205, 170, 125]],
    "burlywood4": ["#8B7355", [139, 115, 85]],
    "burntsienna": ["#8A360F", [138, 54, 15]],
    "burntumber": ["#8A3324", [138, 51, 36]],
    "cadetblue": ["#5F9EA0", [95, 158, 160]],
    "cadetblue1": ["#98F5FF", [152, 245, 255]],
    "cadetblue2": ["#8EE5EE", [142, 229, 238]],
    "cadetblue3": ["#7AC5CD", [122, 197, 205]],
    "cadetblue4": ["#53868B", [83, 134, 139]],
    "cadmiumorange": ["#FF6103", [255, 97, 3]],
    "cadmiumyellow": ["#FF9912", [255, 153, 18]],
    "carrot": ["#ED9121", [237, 145, 33]],
    "chartreuse": ["#DFFF00", [223, 255, 0]],
    "chartreuse1": ["#7FFF00", [127, 255, 0]],
    "chartreuse2": ["#76EE00", [118, 238, 0]],
    "chartreuse3": ["#66CD00", [102, 205, 0]],
    "chartreuse4": ["#458B00", [69, 139, 0]],
    "chocolate": ["#D2691E", [210, 105, 30]],
    "chocolate1": ["#FF7F24", [255, 127, 36]],
    "chocolate2": ["#EE7621", [238, 118, 33]],
    "chocolate3": ["#CD661D", [205, 102, 29]],
    "chocolate4": ["#8B4513", [139, 69, 19]],
    "cobalt": ["#3D59AB", [61, 89, 171]],
    "cobaltgreen": ["#3D9140", [61, 145, 64]],
    "coldgrey": ["#808A87", [128, 138, 135]],
    "coral": ["#FF7F50", [255, 127, 80]],
    "coral1": ["#FF7256", [255, 114, 86]],
    "coral2": ["#EE6A50", [238, 106, 80]],
    "coral3": ["#CD5B45", [205, 91, 69]],
    "coral4": ["#8B3E2F", [139, 62, 47]],
    "cornflowerblue": ["#6495ED", [100, 149, 237]],
    "cornsilk": ["#FFF8DC", [255, 248, 220]],
    "cornsilk1": ["#FFF8DC", [255, 248, 220]],
    "cornsilk2": ["#EEE8CD", [238, 232, 205]],
    "cornsilk3": ["#CDC8B1", [205, 200, 177]],
    "cornsilk4": ["#8B8878", [139, 136, 120]],
    "crimson": ["#DC143C", [220, 20, 60]],
    "cyan": ["#00FFFF", [0, 255, 255]],
    "cyan2": ["#00EEEE", [0, 238, 238]],
    "cyan3": ["#00CDCD", [0, 205, 205]],
    "cyan4": ["#008B8B", [0, 139, 139]],
    "darkgoldenrod": ["#B8860B", [184, 134, 11]],
    "darkgoldenrod1": ["#FFB90F", [255, 185, 15]],
    "darkgoldenrod2": ["#EEAD0E", [238, 173, 14]],
    "darkgoldenrod3": ["#CD950C", [205, 149, 12]],
    "darkgoldenrod4": ["#8B6508", [139, 101, 8]],
    "darkgray": ["#A9A9A9", [169, 169, 169]],
    "darkgreen": ["#006400", [0, 100, 0]],
    "darkkhaki": ["#BDB76B", [189, 183, 107]],
    "darkolivegreen": ["#556B2F", [85, 107, 47]],
    "darkolivegreen1": ["#CAFF70", [202, 255, 112]],
    "darkolivegreen2": ["#BCEE68", [188, 238, 104]],
    "darkolivegreen3": ["#A2CD5A", [162, 205, 90]],
    "darkolivegreen4": ["#6E8B3D", [110, 139, 61]],
    "darkorange": ["#FF8C00", [255, 140, 0]],
    "darkorange1": ["#FF7F00", [255, 127, 0]],
    "darkorange2": ["#EE7600", [238, 118, 0]],
    "darkorange3": ["#CD6600", [205, 102, 0]],
    "darkorange4": ["#8B4500", [139, 69, 0]],
    "darkorchid": ["#9932CC", [153, 50, 204]],
    "darkorchid1": ["#BF3EFF", [191, 62, 255]],
    "darkorchid2": ["#B23AEE", [178, 58, 238]],
    "darkorchid3": ["#9A32CD", [154, 50, 205]],
    "darkorchid4": ["#68228B", [104, 34, 139]],
    "darksalmon": ["#E9967A", [233, 150, 122]],
    "darkseagreen": ["#8FBC8F", [143, 188, 143]],
    "darkseagreen1": ["#C1FFC1", [193, 255, 193]],
    "darkseagreen2": ["#B4EEB4", [180, 238, 180]],
    "darkseagreen3": ["#9BCD9B", [155, 205, 155]],
    "darkseagreen4": ["#698B69", [105, 139, 105]],
    "darkslateblue": ["#483D8B", [72, 61, 139]],
    "darkslategray": ["#2F4F4F", [47, 79, 79]],
    "darkslategray1": ["#97FFFF", [151, 255, 255]],
    "darkslategray2": ["#8DEEEE", [141, 238, 238]],
    "darkslategray3": ["#79CDCD", [121, 205, 205]],
    "darkslategray4": ["#528B8B", [82, 139, 139]],
    "darkturquoise": ["#00CED1", [0, 206, 209]],
    "darkviolet": ["#9400D3", [148, 0, 211]],
    "deeppink1": ["#FF1493", [255, 20, 147]],
    "deeppink2": ["#EE1289", [238, 18, 137]],
    "deeppink3": ["#CD1076", [205, 16, 118]],
    "deeppink4": ["#8B0A50", [139, 10, 80]],
    "deepskyblue": ["#00BFFF", [0, 191, 255]],
    "deepskyblue1": ["#00BFFF", [0, 191, 255]],
    "deepskyblue2": ["#00B2EE", [0, 178, 238]],
    "deepskyblue3": ["#009ACD", [0, 154, 205]],
    "deepskyblue4": ["#00688B", [0, 104, 139]],
    "dimgray": ["#696969", [105, 105, 105]],
    "dodgerblue1": ["#1E90FF", [30, 144, 255]],
    "dodgerblue2": ["#1C86EE", [28, 134, 238]],
    "dodgerblue3": ["#1874CD", [24, 116, 205]],
    "dodgerblue4": ["#104E8B", [16, 78, 139]],
    "eggshell": ["#FCE6C9", [252, 230, 201]],
    "emeraldgreen": ["#00C957", [0, 201, 87]],
    "firebrick": ["#B22222", [178, 34, 34]],
    "firebrick1": ["#FF3030", [255, 48, 48]],
    "firebrick2": ["#EE2C2C", [238, 44, 44]],
    "firebrick3": ["#CD2626", [205, 38, 38]],
    "firebrick4": ["#8B1A1A", [139, 26, 26]],
    "flesh": ["#FF7D40", [255, 125, 64]],
    "floralwhite": ["#FFFAF0", [255, 250, 240]],
    "forestgreen": ["#228B22", [34, 139, 34]],
    "gainsboro": ["#DCDCDC", [220, 220, 220]],
    "ghostwhite": ["#F8F8FF", [248, 248, 255]],
    "gold1": ["#FFD700", [255, 215, 0]],
    "gold2": ["#EEC900", [238, 201, 0]],
    "gold3": ["#CDAD00", [205, 173, 0]],
    "gold4": ["#8B7500", [139, 117, 0]],
    "goldenrod": ["#DAA520", [218, 165, 32]],
    "goldenrod1": ["#FFC125", [255, 193, 37]],
    "goldenrod2": ["#EEB422", [238, 180, 34]],
    "goldenrod3": ["#CD9B1D", [205, 155, 29]],
    "goldenrod4": ["#8B6914", [139, 105, 20]],
    "gray": ["#808080", [128, 128, 128]],
    "gray1": ["#030303", [3, 3, 3]],
    "gray10": ["#1A1A1A", [26, 26, 26]],
    "gray11": ["#1C1C1C", [28, 28, 28]],
    "gray12": ["#1F1F1F", [31, 31, 31]],
    "gray13": ["#212121", [33, 33, 33]],
    "gray14": ["#242424", [36, 36, 36]],
    "gray15": ["#262626", [38, 38, 38]],
    "gray16": ["#292929", [41, 41, 41]],
    "gray17": ["#2B2B2B", [43, 43, 43]],
    "gray18": ["#2E2E2E", [46, 46, 46]],
    "gray19": ["#303030", [48, 48, 48]],
    "gray2": ["#050505", [5, 5, 5]],
    "gray20": ["#333333", [51, 51, 51]],
    "gray21": ["#363636", [54, 54, 54]],
    "gray22": ["#383838", [56, 56, 56]],
    "gray23": ["#3B3B3B", [59, 59, 59]],
    "gray24": ["#3D3D3D", [61, 61, 61]],
    "gray25": ["#404040", [64, 64, 64]],
    "gray26": ["#424242", [66, 66, 66]],
    "gray27": ["#454545", [69, 69, 69]],
    "gray28": ["#474747", [71, 71, 71]],
    "gray29": ["#4A4A4A", [74, 74, 74]],
    "gray3": ["#080808", [8, 8, 8]],
    "gray30": ["#4D4D4D", [77, 77, 77]],
    "gray31": ["#4F4F4F", [79, 79, 79]],
    "gray32": ["#525252", [82, 82, 82]],
    "gray33": ["#545454", [84, 84, 84]],
    "gray34": ["#575757", [87, 87, 87]],
    "gray35": ["#595959", [89, 89, 89]],
    "gray36": ["#5C5C5C", [92, 92, 92]],
    "gray37": ["#5E5E5E", [94, 94, 94]],
    "gray38": ["#616161", [97, 97, 97]],
    "gray39": ["#636363", [99, 99, 99]],
    "gray4": ["#0A0A0A", [10, 10, 10]],
    "gray40": ["#666666", [102, 102, 102]],
    "gray42": ["#6B6B6B", [107, 107, 107]],
    "gray43": ["#6E6E6E", [110, 110, 110]],
    "gray44": ["#707070", [112, 112, 112]],
    "gray45": ["#737373", [115, 115, 115]],
    "gray46": ["#757575", [117, 117, 117]],
    "gray47": ["#787878", [120, 120, 120]],
    "gray48": ["#7A7A7A", [122, 122, 122]],
    "gray49": ["#7D7D7D", [125, 125, 125]],
    "gray5": ["#0D0D0D", [13, 13, 13]],
    "gray50": ["#7F7F7F", [127, 127, 127]],
    "gray51": ["#828282", [130, 130, 130]],
    "gray52": ["#858585", [133, 133, 133]],
    "gray53": ["#878787", [135, 135, 135]],
    "gray54": ["#8A8A8A", [138, 138, 138]],
    "gray55": ["#8C8C8C", [140, 140, 140]],
    "gray56": ["#8F8F8F", [143, 143, 143]],
    "gray57": ["#919191", [145, 145, 145]],
    "gray58": ["#949494", [148, 148, 148]],
    "gray59": ["#969696", [150, 150, 150]],
    "gray6": ["#0F0F0F", [15, 15, 15]],
    "gray60": ["#999999", [153, 153, 153]],
    "gray61": ["#9C9C9C", [156, 156, 156]],
    "gray62": ["#9E9E9E", [158, 158, 158]],
    "gray63": ["#A1A1A1", [161, 161, 161]],
    "gray64": ["#A3A3A3", [163, 163, 163]],
    "gray65": ["#A6A6A6", [166, 166, 166]],
    "gray66": ["#A8A8A8", [168, 168, 168]],
    "gray67": ["#ABABAB", [171, 171, 171]],
    "gray68": ["#ADADAD", [173, 173, 173]],
    "gray69": ["#B0B0B0", [176, 176, 176]],
    "gray7": ["#121212", [18, 18, 18]],
    "gray70": ["#B3B3B3", [179, 179, 179]],
    "gray71": ["#B5B5B5", [181, 181, 181]],
    "gray72": ["#B8B8B8", [184, 184, 184]],
    "gray73": ["#BABABA", [186, 186, 186]],
    "gray74": ["#BDBDBD", [189, 189, 189]],
    "gray75": ["#BFBFBF", [191, 191, 191]],
    "gray76": ["#C2C2C2", [194, 194, 194]],
    "gray77": ["#C4C4C4", [196, 196, 196]],
    "gray78": ["#C7C7C7", [199, 199, 199]],
    "gray79": ["#C9C9C9", [201, 201, 201]],
    "gray8": ["#141414", [20, 20, 20]],
    "gray80": ["#CCCCCC", [204, 204, 204]],
    "gray81": ["#CFCFCF", [207, 207, 207]],
    "gray82": ["#D1D1D1", [209, 209, 209]],
    "gray83": ["#D4D4D4", [212, 212, 212]],
    "gray84": ["#D6D6D6", [214, 214, 214]],
    "gray85": ["#D9D9D9", [217, 217, 217]],
    "gray86": ["#DBDBDB", [219, 219, 219]],
    "gray87": ["#DEDEDE", [222, 222, 222]],
    "gray88": ["#E0E0E0", [224, 224, 224]],
    "gray89": ["#E3E3E3", [227, 227, 227]],
    "gray9": ["#171717", [23, 23, 23]],
    "gray90": ["#E5E5E5", [229, 229, 229]],
    "gray91": ["#E8E8E8", [232, 232, 232]],
    "gray92": ["#EBEBEB", [235, 235, 235]],
    "gray93": ["#EDEDED", [237, 237, 237]],
    "gray94": ["#F0F0F0", [240, 240, 240]],
    "gray95": ["#F2F2F2", [242, 242, 242]],
    "gray97": ["#F7F7F7", [247, 247, 247]],
    "gray98": ["#FAFAFA", [250, 250, 250]],
    "gray99": ["#FCFCFC", [252, 252, 252]],
    "green": ["#008000", [0, 128, 0]],
    "green1": ["#00FF00", [0, 255, 0]],
    "green2": ["#00EE00", [0, 238, 0]],
    "green3": ["#00CD00", [0, 205, 0]],
    "green4": ["#008B00", [0, 139, 0]],
    "greenyellow": ["#ADFF2F", [173, 255, 47]],
    "honeydew1": ["#F0FFF0", [240, 255, 240]],
    "honeydew2": ["#E0EEE0", [224, 238, 224]],
    "honeydew3": ["#C1CDC1", [193, 205, 193]],
    "honeydew4": ["#838B83", [131, 139, 131]],
    "hotpink": ["#FF69B4", [255, 105, 180]],
    "hotpink1": ["#FF6EB4", [255, 110, 180]],
    "hotpink2": ["#EE6AA7", [238, 106, 167]],
    "hotpink3": ["#CD6090", [205, 96, 144]],
    "hotpink4": ["#8B3A62", [139, 58, 98]],
    "indianred": ["#CD5C5C", [205, 92, 92]],
    "indianred1": ["#FF6A6A", [255, 106, 106]],
    "indianred2": ["#EE6363", [238, 99, 99]],
    "indianred3": ["#CD5555", [205, 85, 85]],
    "indianred4": ["#8B3A3A", [139, 58, 58]],
    "indigo": ["#4B0082", [75, 0, 130]],
    "ivory1": ["#FFFFF0", [255, 255, 240]],
    "ivory2": ["#EEEEE0", [238, 238, 224]],
    "ivory3": ["#CDCDC1", [205, 205, 193]],
    "ivory4": ["#8B8B83", [139, 139, 131]],
    "ivoryblack": ["#292421", [41, 36, 33]],
    "khaki": ["#F0E68C", [240, 230, 140]],
    "khaki1": ["#FFF68F", [255, 246, 143]],
    "khaki2": ["#EEE685", [238, 230, 133]],
    "khaki3": ["#CDC673", [205, 198, 115]],
    "khaki4": ["#8B864E", [139, 134, 78]],
    "lavender": ["#E6E6FA", [230, 230, 250]],
    "lavenderblush1": ["#FFF0F5", [255, 240, 245]],
    "lavenderblush2": ["#EEE0E5", [238, 224, 229]],
    "lavenderblush3": ["#CDC1C5", [205, 193, 197]],
    "lavenderblush4": ["#8B8386", [139, 131, 134]],
    "lawngreen": ["#7CFC00", [124, 252, 0]],
    "lemonchiffon1": ["#FFFACD", [255, 250, 205]],
    "lemonchiffon2": ["#EEE9BF", [238, 233, 191]],
    "lemonchiffon3": ["#CDC9A5", [205, 201, 165]],
    "lemonchiffon4": ["#8B8970", [139, 137, 112]],
    "lightblue": ["#ADD8E6", [173, 216, 230]],
    "lightblue1": ["#BFEFFF", [191, 239, 255]],
    "lightblue2": ["#B2DFEE", [178, 223, 238]],
    "lightblue3": ["#9AC0CD", [154, 192, 205]],
    "lightblue4": ["#68838B", [104, 131, 139]],
    "lightcoral": ["#F08080", [240, 128, 128]],
    "lightcyan1": ["#E0FFFF", [224, 255, 255]],
    "lightcyan2": ["#D1EEEE", [209, 238, 238]],
    "lightcyan3": ["#B4CDCD", [180, 205, 205]],
    "lightcyan4": ["#7A8B8B", [122, 139, 139]],
    "lightgoldenrod1": ["#FFEC8B", [255, 236, 139]],
    "lightgoldenrod2": ["#EEDC82", [238, 220, 130]],
    "lightgoldenrod3": ["#CDBE70", [205, 190, 112]],
    "lightgoldenrod4": ["#8B814C", [139, 129, 76]],
    "lightgoldenrodyellow": ["#FAFAD2", [250, 250, 210]],
    "lightgrey": ["#D3D3D3", [211, 211, 211]],
    "lightpink": ["#FFB6C1", [255, 182, 193]],
    "lightpink1": ["#FFAEB9", [255, 174, 185]],
    "lightpink2": ["#EEA2AD", [238, 162, 173]],
    "lightpink3": ["#CD8C95", [205, 140, 149]],
    "lightpink4": ["#8B5F65", [139, 95, 101]],
    "lightsalmon1": ["#FFA07A", [255, 160, 122]],
    "lightsalmon2": ["#EE9572", [238, 149, 114]],
    "lightsalmon3": ["#CD8162", [205, 129, 98]],
    "lightsalmon4": ["#8B5742", [139, 87, 66]],
    "lightseagreen": ["#20B2AA", [32, 178, 170]],
    "lightskyblue": ["#87CEFA", [135, 206, 250]],
    "lightskyblue1": ["#B0E2FF", [176, 226, 255]],
    "lightskyblue2": ["#A4D3EE", [164, 211, 238]],
    "lightskyblue3": ["#8DB6CD", [141, 182, 205]],
    "lightskyblue4": ["#607B8B", [96, 123, 139]],
    "lightslateblue": ["#8470FF", [132, 112, 255]],
    "lightslategray": ["#778899", [119, 136, 153]],
    "lightsteelblue": ["#B0C4DE", [176, 196, 222]],
    "lightsteelblue1": ["#CAE1FF", [202, 225, 255]],
    "lightsteelblue2": ["#BCD2EE", [188, 210, 238]],
    "lightsteelblue3": ["#A2B5CD", [162, 181, 205]],
    "lightsteelblue4": ["#6E7B8B", [110, 123, 139]],
    "lightyellow1": ["#FFFFE0", [255, 255, 224]],
    "lightyellow2": ["#EEEED1", [238, 238, 209]],
    "lightyellow3": ["#CDCDB4", [205, 205, 180]],
    "lightyellow4": ["#8B8B7A", [139, 139, 122]],
    "limegreen": ["#32CD32", [50, 205, 50]],
    "linen": ["#FAF0E6", [250, 240, 230]],
    "magenta": ["#FF00FF", [255, 0, 255]],
    "magenta2": ["#EE00EE", [238, 0, 238]],
    "magenta3": ["#CD00CD", [205, 0, 205]],
    "magenta4": ["#8B008B", [139, 0, 139]],
    "manganeseblue": ["#03A89E", [3, 168, 158]],
    "maroon": ["#800000", [128, 0, 0]],
    "maroon1": ["#FF34B3", [255, 52, 179]],
    "maroon2": ["#EE30A7", [238, 48, 167]],
    "maroon3": ["#CD2990", [205, 41, 144]],
    "maroon4": ["#8B1C62", [139, 28, 98]],
    "mediumorchid": ["#BA55D3", [186, 85, 211]],
    "mediumorchid1": ["#E066FF", [224, 102, 255]],
    "mediumorchid2": ["#D15FEE", [209, 95, 238]],
    "mediumorchid3": ["#B452CD", [180, 82, 205]],
    "mediumorchid4": ["#7A378B", [122, 55, 139]],
    "mediumpurple": ["#9370DB", [147, 112, 219]],
    "mediumpurple1": ["#AB82FF", [171, 130, 255]],
    "mediumpurple2": ["#9F79EE", [159, 121, 238]],
    "mediumpurple3": ["#8968CD", [137, 104, 205]],
    "mediumpurple4": ["#5D478B", [93, 71, 139]],
    "mediumseagreen": ["#3CB371", [60, 179, 113]],
    "mediumslateblue": ["#7B68EE", [123, 104, 238]],
    "mediumspringgreen": ["#00FA9A", [0, 250, 154]],
    "mediumturquoise": ["#48D1CC", [72, 209, 204]],
    "mediumvioletred": ["#C71585", [199, 21, 133]],
    "melon": ["#E3A869", [227, 168, 105]],
    "midnightblue": ["#191970", [25, 25, 112]],
    "mint": ["#BDFCC9", [189, 252, 201]],
    "mintcream": ["#F5FFFA", [245, 255, 250]],
    "mistyrose1": ["#FFE4E1", [255, 228, 225]],
    "mistyrose2": ["#EED5D2", [238, 213, 210]],
    "mistyrose3": ["#CDB7B5", [205, 183, 181]],
    "mistyrose4": ["#8B7D7B", [139, 125, 123]],
    "moccasin": ["#FFE4B5", [255, 228, 181]],
    "navajowhite1": ["#FFDEAD", [255, 222, 173]],
    "navajowhite2": ["#EECFA1", [238, 207, 161]],
    "navajowhite3": ["#CDB38B", [205, 179, 139]],
    "navajowhite4": ["#8B795E", [139, 121, 94]],
    "navy": ["#000080", [0, 0, 128]],
    "oldlace": ["#FDF5E6", [253, 245, 230]],
    "olive": ["#808000", [128, 128, 0]],
    "olivedrab": ["#6B8E23", [107, 142, 35]],
    "olivedrab1": ["#C0FF3E", [192, 255, 62]],
    "olivedrab2": ["#B3EE3A", [179, 238, 58]],
    "olivedrab3": ["#9ACD32", [154, 205, 50]],
    "olivedrab4": ["#698B22", [105, 139, 34]],
    "orange": ["#FF8000", [255, 128, 0]],
    "orange1": ["#FFA500", [255, 165, 0]],
    "orange2": ["#EE9A00", [238, 154, 0]],
    "orange3": ["#CD8500", [205, 133, 0]],
    "orange4": ["#8B5A00", [139, 90, 0]],
    "orangered1": ["#FF4500", [255, 69, 0]],
    "orangered2": ["#EE4000", [238, 64, 0]],
    "orangered3": ["#CD3700", [205, 55, 0]],
    "orangered4": ["#8B2500", [139, 37, 0]],
    "orchid": ["#DA70D6", [218, 112, 214]],
    "orchid1": ["#FF83FA", [255, 131, 250]],
    "orchid2": ["#EE7AE9", [238, 122, 233]],
    "orchid3": ["#CD69C9", [205, 105, 201]],
    "orchid4": ["#8B4789", [139, 71, 137]],
    "palegoldenrod": ["#EEE8AA", [238, 232, 170]],
    "palegreen": ["#98FB98", [152, 251, 152]],
    "palegreen1": ["#9AFF9A", [154, 255, 154]],
    "palegreen2": ["#90EE90", [144, 238, 144]],
    "palegreen3": ["#7CCD7C", [124, 205, 124]],
    "palegreen4": ["#548B54", [84, 139, 84]],
    "paleturquoise1": ["#BBFFFF", [187, 255, 255]],
    "paleturquoise2": ["#AEEEEE", [174, 238, 238]],
    "paleturquoise3": ["#96CDCD", [150, 205, 205]],
    "paleturquoise4": ["#668B8B", [102, 139, 139]],
    "palevioletred": ["#DB7093", [219, 112, 147]],
    "palevioletred1": ["#FF82AB", [255, 130, 171]],
    "palevioletred2": ["#EE799F", [238, 121, 159]],
    "palevioletred3": ["#CD6889", [205, 104, 137]],
    "palevioletred4": ["#8B475D", [139, 71, 93]],
    "papayawhip": ["#FFEFD5", [255, 239, 213]],
    "peachpuff1": ["#FFDAB9", [255, 218, 185]],
    "peachpuff2": ["#EECBAD", [238, 203, 173]],
    "peachpuff3": ["#CDAF95", [205, 175, 149]],
    "peachpuff4": ["#8B7765", [139, 119, 101]],
    "peacock": ["#33A1C9", [51, 161, 201]],
    "pink": ["#FFC0CB", [255, 192, 203]],
    "pink1": ["#FFB5C5", [255, 181, 197]],
    "pink2": ["#EEA9B8", [238, 169, 184]],
    "pink3": ["#CD919E", [205, 145, 158]],
    "pink4": ["#8B636C", [139, 99, 108]],
    "plum": ["#DDA0DD", [221, 160, 221]],
    "plum1": ["#FFBBFF", [255, 187, 255]],
    "plum2": ["#EEAEEE", [238, 174, 238]],
    "plum3": ["#CD96CD", [205, 150, 205]],
    "plum4": ["#8B668B", [139, 102, 139]],
    "powderblue": ["#B0E0E6", [176, 224, 230]],
    "purple": ["#800080", [128, 0, 128]],
    "purple1": ["#9B30FF", [155, 48, 255]],
    "purple2": ["#912CEE", [145, 44, 238]],
    "purple3": ["#7D26CD", [125, 38, 205]],
    "purple4": ["#551A8B", [85, 26, 139]],
    "raspberry": ["#872657", [135, 38, 87]],
    "rawsienna": ["#C76114", [199, 97, 20]],
    "red1": ["#FF0000", [255, 0, 0]],
    "red2": ["#EE0000", [238, 0, 0]],
    "red3": ["#CD0000", [205, 0, 0]],
    "red4": ["#8B0000", [139, 0, 0]],
    "rosybrown": ["#BC8F8F", [188, 143, 143]],
    "rosybrown1": ["#FFC1C1", [255, 193, 193]],
    "rosybrown2": ["#EEB4B4", [238, 180, 180]],
    "rosybrown3": ["#CD9B9B", [205, 155, 155]],
    "rosybrown4": ["#8B6969", [139, 105, 105]],
    "royalblue": ["#4169E1", [65, 105, 225]],
    "royalblue1": ["#4876FF", [72, 118, 255]],
    "royalblue2": ["#436EEE", [67, 110, 238]],
    "royalblue3": ["#3A5FCD", [58, 95, 205]],
    "royalblue4": ["#27408B", [39, 64, 139]],
    "salmon": ["#FA8072", [250, 128, 114]],
    "salmon1": ["#FF8C69", [255, 140, 105]],
    "salmon2": ["#EE8262", [238, 130, 98]],
    "salmon3": ["#CD7054", [205, 112, 84]],
    "salmon4": ["#8B4C39", [139, 76, 57]],
    "sandybrown": ["#F4A460", [244, 164, 96]],
    "sapgreen": ["#308014", [48, 128, 20]],
    "seagreen1": ["#54FF9F", [84, 255, 159]],
    "seagreen2": ["#4EEE94", [78, 238, 148]],
    "seagreen3": ["#43CD80", [67, 205, 128]],
    "seagreen4": ["#2E8B57", [46, 139, 87]],
    "seashell1": ["#FFF5EE", [255, 245, 238]],
    "seashell2": ["#EEE5DE", [238, 229, 222]],
    "seashell3": ["#CDC5BF", [205, 197, 191]],
    "seashell4": ["#8B8682", [139, 134, 130]],
    "sepia": ["#5E2612", [94, 38, 18]],
    "sgibeet": ["#8E388E", [142, 56, 142]],
    "sgibrightgray": ["#C5C1AA", [197, 193, 170]],
    "sgichartreuse": ["#71C671", [113, 198, 113]],
    "sgidarkgray": ["#555555", [85, 85, 85]],
    "sgigray12": ["#1E1E1E", [30, 30, 30]],
    "sgigray16": ["#282828", [40, 40, 40]],
    "sgigray32": ["#515151", [81, 81, 81]],
    "sgigray36": ["#5B5B5B", [91, 91, 91]],
    "sgigray52": ["#848484", [132, 132, 132]],
    "sgigray56": ["#8E8E8E", [142, 142, 142]],
    "sgigray72": ["#B7B7B7", [183, 183, 183]],
    "sgigray76": ["#C1C1C1", [193, 193, 193]],
    "sgigray92": ["#EAEAEA", [234, 234, 234]],
    "sgigray96": ["#F4F4F4", [244, 244, 244]],
    "sgilightblue": ["#7D9EC0", [125, 158, 192]],
    "sgilightgray": ["#AAAAAA", [170, 170, 170]],
    "sgiolivedrab": ["#8E8E38", [142, 142, 56]],
    "sgisalmon": ["#C67171", [198, 113, 113]],
    "sgislateblue": ["#7171C6", [113, 113, 198]],
    "sgiteal": ["#388E8E", [56, 142, 142]],
    "sienna": ["#A0522D", [160, 82, 45]],
    "sienna1": ["#FF8247", [255, 130, 71]],
    "sienna2": ["#EE7942", [238, 121, 66]],
    "sienna3": ["#CD6839", [205, 104, 57]],
    "sienna4": ["#8B4726", [139, 71, 38]],
    "silver": ["#C0C0C0", [192, 192, 192]],
    "skyblue": ["#87CEEB", [135, 206, 235]],
    "skyblue1": ["#87CEFF", [135, 206, 255]],
    "skyblue2": ["#7EC0EE", [126, 192, 238]],
    "skyblue3": ["#6CA6CD", [108, 166, 205]],
    "skyblue4": ["#4A708B", [74, 112, 139]],
    "slateblue": ["#6A5ACD", [106, 90, 205]],
    "slateblue1": ["#836FFF", [131, 111, 255]],
    "slateblue2": ["#7A67EE", [122, 103, 238]],
    "slateblue3": ["#6959CD", [105, 89, 205]],
    "slateblue4": ["#473C8B", [71, 60, 139]],
    "slategray": ["#708090", [112, 128, 144]],
    "slategray1": ["#C6E2FF", [198, 226, 255]],
    "slategray2": ["#B9D3EE", [185, 211, 238]],
    "slategray3": ["#9FB6CD", [159, 182, 205]],
    "slategray4": ["#6C7B8B", [108, 123, 139]],
    "snow1": ["#FFFAFA", [255, 250, 250]],
    "snow2": ["#EEE9E9", [238, 233, 233]],
    "snow3": ["#CDC9C9", [205, 201, 201]],
    "snow4": ["#8B8989", [139, 137, 137]],
    "springgreen": ["#00FF7F", [0, 255, 127]],
    "springgreen1": ["#00EE76", [0, 238, 118]],
    "springgreen2": ["#00CD66", [0, 205, 102]],
    "springgreen3": ["#008B45", [0, 139, 69]],
    "steelblue": ["#4682B4", [70, 130, 180]],
    "steelblue1": ["#63B8FF", [99, 184, 255]],
    "steelblue2": ["#5CACEE", [92, 172, 238]],
    "steelblue3": ["#4F94CD", [79, 148, 205]],
    "steelblue4": ["#36648B", [54, 100, 139]],
    "tan": ["#D2B48C", [210, 180, 140]],
    "tan1": ["#FFA54F", [255, 165, 79]],
    "tan2": ["#EE9A49", [238, 154, 73]],
    "tan3": ["#CD853F", [205, 133, 63]],
    "tan4": ["#8B5A2B", [139, 90, 43]],
    "teal": ["#008080", [0, 128, 128]],
    "thistle": ["#D8BFD8", [216, 191, 216]],
    "thistle1": ["#FFE1FF", [255, 225, 255]],
    "thistle2": ["#EED2EE", [238, 210, 238]],
    "thistle3": ["#CDB5CD", [205, 181, 205]],
    "thistle4": ["#8B7B8B", [139, 123, 139]],
    "tomato1": ["#FF6347", [255, 99, 71]],
    "tomato2": ["#EE5C42", [238, 92, 66]],
    "tomato3": ["#CD4F39", [205, 79, 57]],
    "tomato4": ["#8B3626", [139, 54, 38]],
    "turquoise": ["#40E0D0", [64, 224, 208]],
    "turquoise1": ["#00F5FF", [0, 245, 255]],
    "turquoise2": ["#00E5EE", [0, 229, 238]],
    "turquoise3": ["#00C5CD", [0, 197, 205]],
    "turquoise4": ["#00868B", [0, 134, 139]],
    "turquoiseblue": ["#00C78C", [0, 199, 140]],
    "violet": ["#EE82EE", [238, 130, 238]],
    "violetred": ["#D02090", [208, 32, 144]],
    "violetred1": ["#FF3E96", [255, 62, 150]],
    "violetred2": ["#EE3A8C", [238, 58, 140]],
    "violetred3": ["#CD3278", [205, 50, 120]],
    "violetred4": ["#8B2252", [139, 34, 82]],
    "warmgrey": ["#808069", [128, 128, 105]],
    "wheat": ["#F5DEB3", [245, 222, 179]],
    "wheat1": ["#FFE7BA", [255, 231, 186]],
    "wheat2": ["#EED8AE", [238, 216, 174]],
    "wheat3": ["#CDBA96", [205, 186, 150]],
    "wheat4": ["#8B7E66", [139, 126, 102]],
    "white": ["#FFFFFF", [255, 255, 255]],
    "whitesmoke": ["#F5F5F5", [245, 245, 245]],
    "yellow1": ["#FFFF00", [255, 255, 0]],
    "yellow2": ["#EEEE00", [238, 238, 0]],
    "yellow3": ["#CDCD00", [205, 205, 0]],
    "yellow4": ["#8B8B00", [139, 139, 0]],
}
