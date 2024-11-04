import os
from PIL import Image, ImageOps

images_path = '/home/jam/Gits/manuscript_analysis_project/scraper/Downloads/'

images = os.listdir(images_path)

dims = []
for f in images:
    filepath = f'/home/jam/Gits/manuscript_analysis_project/scraper/Downloads/{f}'
    img = Image.open(filepath)
    # get width and height
    width = img.width
    height = img.height
    print(width, height, f)
    dims.append((width, height))

if len(set(dims)) > 1:
    print("The image set has varying dimensions")




def resize_and_pad(image, target_size):
    # Resize the image while maintaining aspect ratio
    image.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)

    # Calculate padding to make the image square
    delta_width = target_size - image.size[0]
    delta_height = target_size - image.size[1]
    padding = (delta_width // 2, delta_height // 2, delta_width - (delta_width // 2), delta_height - (delta_height // 2))

    # Add padding
    new_image = ImageOps.expand(image, padding, fill="black")

    return new_image

# Example usage
result = resize_and_pad(img, 256)  # Resizes and pads the image to 256x256 pixels
result.show()  # or result.save("output.jpg")
