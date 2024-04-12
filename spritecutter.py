from PIL import Image
import pygame

def split_image_into_frames(image_path, grid_size=3, crop_size=0, scale_factor=0.5):
    """
    Splits an image with a grid of sprites into individual frames, 
    checking for alpha channel or using black as the transparent color.
    Each frame is then cropped, scaled, and converted into a Pygame surface.

    :param image_path: Path to the input image.
    :param grid_size: The size of the grid (default 3 for a 3x3 grid).
    :param crop_size: Amount to crop from each side of each frame.
    :param scale_factor: Factor by which to scale the size of each frame.
    :return: List of Pygame surfaces (frames).
    """
    with Image.open(image_path) as img:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        width, height = img.size
        cell_size = width // grid_size
        new_size = cell_size - 2 * crop_size

        frames = []
        for i in range(grid_size):
            for j in range(grid_size):
                left = j * cell_size + crop_size
                upper = i * cell_size + crop_size
                right = left + new_size
                lower = upper + new_size

                frame = img.crop((left, upper, right, lower))
                
                # If the image does not have transparency, make black (0,0,0) transparent
                if 'A' not in frame.getbands():
                    # Create an alpha channel with transparency set where the pixels are black
                    datas = frame.getdata()
                    newData = []
                    for item in datas:
                        # Change all black (also nearly black) pixels to transparent
                        if item[0] == 0 and item[1] == 0 and item[2] == 0:
                            newData.append((255, 255, 255, 0))
                        else:
                            newData.append(item)
                    frame.putdata(newData)

                if scale_factor != 1.0:
                    # Resize the frame according to the scale factor
                    scaled_size = (int(new_size * scale_factor), int(new_size * scale_factor))
                    frame = frame.resize(scaled_size, Image.Resampling.LANCZOS)
                
                # Convert the frame to a string buffer and then to a Pygame surface
                frame_surface = pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode)
                frames.append(frame_surface)

        return frames
