# Crop banner image top and bottom using PIL
from PIL import Image

# Load the image
img = Image.open('studymate_banner.png.png')

# Get image size
width, height = img.size

# Define crop box (remove 15% from top and bottom)
top_crop = int(height * 0.15)
bottom_crop = int(height * 0.85)
crop_box = (0, top_crop, width, bottom_crop)

# Crop and save
cropped_img = img.crop(crop_box)
cropped_img.save('studymate_banner.png')
print('Banner image cropped and saved as studymate_banner.png')
