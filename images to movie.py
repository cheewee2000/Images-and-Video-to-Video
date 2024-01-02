import cv2
import os
import moviepy.editor as mpy
from PIL import Image
import datetime


# Directory of images and videos
WORKING_DIR = '/Users/cwwang/Dropbox/My Mac (9.local)/Desktop/2023 recap'
# Output video resolution
WIDTH, HEIGHT = 1080, 1920
FPS = 30


# Image and video clip durations
IMAGE_DURATION = 0.03  # duration of each image clip in seconds
VIDEO_CLIP_DURATION = .5  # duration of each video clip in seconds


# Temporary directory for processed videos
TEMP_DIR = os.path.join(WORKING_DIR, 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)


# Function to process image files
def process_image(file):
    with Image.open(file) as img:
        # Handle orientation
        if hasattr(img, '_getexif'):
            exif_data = img._getexif()
            if exif_data is not None:
                for tag, value in exif_data.items():
                    if tag == 274: # 'Orientation' tag
                        if value == 3:   # Rotated 180 degrees
                            img = img.rotate(180)
                        elif value == 6: # Rotated 90 degrees to the right
                            img = img.rotate(-90)
                        elif value == 8: # Rotated 90 degrees to the left
                            img = img.rotate(90)

        # Calculate aspect ratios
        aspect = img.width / img.height  # original aspect ratio
        new_aspect = WIDTH / HEIGHT  # desired aspect ratio

        if aspect > new_aspect:
            # If image is wider than the desired aspect ratio
            new_width = int(HEIGHT * aspect)
            img = img.resize((new_width, HEIGHT), Image.LANCZOS)
        else:
            # If image is taller than the desired aspect ratio
            new_height = int(WIDTH / aspect)
            img = img.resize((WIDTH, new_height), Image.LANCZOS)

        # Crop to desired size
        width, height = img.size
        left = (width - WIDTH)/2
        top = (height - HEIGHT)/2
        right = (width + WIDTH)/2
        bottom = (height + HEIGHT)/2
        img = img.crop((left, top, right, bottom))
        
        img.save(file)



files = sorted(os.listdir(WORKING_DIR),
               key=lambda x: os.path.getctime(os.path.join(WORKING_DIR, x)))  # getctime for creation time

processed_files = []
for file in files:
    file_path = os.path.join(WORKING_DIR, file)
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        process_image(file_path)
        processed_files.append(file_path)

# Create image clips
image_clips = [mpy.ImageClip(m).set_duration(IMAGE_DURATION).set_fps(FPS) for m in processed_files if m.lower().endswith(('.png', '.jpg', '.jpeg'))]

# Concatenate all clips
final_clip = mpy.concatenate_videoclips(image_clips)

# Write the result to a file in the working directory
output_path = os.path.join(WORKING_DIR, "output.mp4")
final_clip.write_videofile(output_path, codec='libx264', fps=FPS)