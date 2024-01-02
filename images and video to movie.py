import cv2
import os
import moviepy.editor as mpy
from PIL import Image, ExifTags
import datetime
import random
import os

# Directory of images and videos
WORKING_DIR = '/Users/cwwang/Dropbox/My Mac (9.local)/Desktop/videos'
# Output video resolution
WIDTH, HEIGHT = 1080, 1920
FPS = 30

# Image and video clip durations
IMAGE_DURATION = 0.1  # duration of each image clip in seconds
VIDEO_CLIP_DURATION = .5  # duration of each video clip in seconds

# Temporary directory for processed videos
TEMP_DIR = os.path.join(WORKING_DIR, 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

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
            new_height = HEIGHT
            new_width = int(new_height * aspect)
        else:
            # If image is taller than the desired aspect ratio
            new_width = WIDTH
            new_height = int(new_width / aspect)

        # Resize image
        img = img.resize((new_width, new_height), Image.LANCZOS)

        # Crop to desired size
        left = (img.width - WIDTH) / 2
        top = (img.height - HEIGHT) / 2
        right = (img.width + WIDTH) / 2
        bottom = (img.height + HEIGHT) / 2
        img = img.crop((left, top, right, bottom))

        img.save(file)

def process_video(file):
    clip = mpy.VideoFileClip(file)
    clip_duration = clip.duration

    # Define minimum and maximum durations for the video clip
    MIN_VIDEO_CLIP_DURATION = 0.25
    MAX_VIDEO_CLIP_DURATION = 1.00

    # Choose a random duration within the range
    VIDEO_CLIP_DURATION = random.uniform(MIN_VIDEO_CLIP_DURATION, MAX_VIDEO_CLIP_DURATION)

    mid_time = clip_duration / 2

    if clip_duration < VIDEO_CLIP_DURATION:  # if the video is less than the clip duration
        start_time = 0
        end_time = clip_duration
    else:
        start_time = mid_time - VIDEO_CLIP_DURATION / 2
        end_time = mid_time + VIDEO_CLIP_DURATION / 2

    clip = clip.subclip(start_time, end_time)  # get the clip from the middle

    # Crop to desired aspect ratio
    if clip.size[0] / clip.size[1] > WIDTH / HEIGHT:
        new_height = clip.size[1]
        new_width = new_height * WIDTH / HEIGHT
    else:
        new_width = clip.size[0]
        new_height = new_width * HEIGHT / WIDTH
    clip = clip.crop(
        x_center=clip.size[0] / 2,
        y_center=clip.size[1] / 2,
        width=int(new_width),
        height=int(new_height),
    )
    
    # Write to a new file in the temporary directory
    new_file = os.path.join(TEMP_DIR, os.path.basename(file))
    
    clip = clip.resize(height=HEIGHT)
    clip.write_videofile(new_file, codec='libx264', audio_codec='aac')
    
    return new_file  # return string, not tuple

files = os.listdir(WORKING_DIR)

# Process files and create image and video clips
processed_files = []
for file in files:
    file_path = os.path.join(WORKING_DIR, file)
    timestamp = os.stat(file_path).st_birthtime
    if file.lower().endswith(('.png', '.jpg', '.jpeg')):
        process_image(file_path)
        processed_files.append((file_path, timestamp))  # store file path and timestamp
    elif file.lower().endswith(('.mp4', '.mov')):
        new_file = process_video(file_path)
        processed_files.append((new_file, timestamp))  # store new file path and original timestamp

clips = []
for file_path, timestamp in processed_files:
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        clip = mpy.ImageClip(file_path).set_duration(IMAGE_DURATION).set_fps(FPS).resize((WIDTH, HEIGHT))
        clips.append((timestamp, clip))  # store timestamp and clip
    elif file_path.lower().endswith(('.mp4', '.mov')):
        clip = mpy.VideoFileClip(file_path)
        clips.append((timestamp, clip))  # store timestamp and clip

# Sort clips based on timestamp
clips.sort()

# Extract sorted clips
sorted_clips = [clip for timestamp, clip in clips]

# Concatenate all clips
final_clip = mpy.concatenate_videoclips(sorted_clips, method='compose')

# Resize the final clip to the desired output video resolution
final_clip = final_clip.resize(height=HEIGHT)

# Write the result to a file in the working directory
output_path = os.path.join(WORKING_DIR, "output.mp4")
final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=FPS)
