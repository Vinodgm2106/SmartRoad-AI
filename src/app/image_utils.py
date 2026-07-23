from PIL import ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS

def get_image_gps(image):
    """
    Extract latitude and longitude from image EXIF metadata.
    Returns (lat, lon) or (None, None) if not present.
    """
    try:
        exif = image._getexif()
        if not exif:
            return None, None
            
        gps_info = {}
        for key, val in exif.items():
            tag = TAGS.get(key, key)
            if tag == "GPSInfo":
                for sub_key, sub_val in val.items():
                    sub_tag = GPSTAGS.get(sub_key, sub_key)
                    gps_info[sub_tag] = sub_val
                    
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")
            
            lat = gps_info["GPSLatitude"]
            lon = gps_info["GPSLongitude"]
            
            # Convert degrees, minutes, seconds to decimal degrees
            lat_dec = float(lat[0]) + float(lat[1])/60.0 + float(lat[2])/3600.0
            lon_dec = float(lon[0]) + float(lon[1])/60.0 + float(lon[2])/3600.0
            
            if lat_ref == "S":
                lat_dec = -lat_dec
            if lon_ref == "W":
                lon_dec = -lon_dec
                
            return lat_dec, lon_dec
    except Exception:
        pass
    return None, None


def annotate_image(image, detections):
    """
    Draws bounding boxes and labels on the image for each detection.
    """
    # Create a copy so we do not mutate the original image in place
    annotated = image.copy()
    draw = ImageDraw.Draw(annotated)

    # Class colors:
    # pothole -> Red
    # longitudinal_crack -> Orange
    # lateral_crack -> Yellow
    # alligator_crack -> Purple
    colors = {
        "pothole": "#EF4444",
        "longitudinal_crack": "#F97316",
        "lateral_crack": "#F59E0B",
        "alligator_crack": "#A855F7"
    }

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for d in detections:
        box = d.get("box")
        if not box:
            continue

        x1, y1, x2, y2 = box
        class_name = d["class_name"]
        conf = d["confidence"]

        color = colors.get(class_name, "#3B82F6")

        # Draw box
        draw.rectangle([x1, y1, x2, y2], outline=color, width=4)

        # Draw label
        label = f"{class_name} ({conf:.1%})"
        
        # Try to draw text background label for readability
        try:
            if hasattr(draw, "textbbox"):
                text_w, text_h = draw.textbbox((0, 0), label, font=font)[2:]
            else:
                text_w, text_h = draw.textsize(label, font=font)
            
            draw.rectangle([x1, y1 - text_h - 4, x1 + text_w + 6, y1], fill=color)
            draw.text((x1 + 3, y1 - text_h - 2), label, fill="white", font=font)
        except Exception:
            # Fallback text draw
            draw.text((x1 + 5, y1 + 5), label, fill=color)

    return annotated
