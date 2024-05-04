import cv2
import numpy as np

def embed_image(video_path, image_path):
    # Read the video
    cap = cv2.VideoCapture(video_path)

    # Read the image to be embedded
    image = cv2.imread(image_path)

    # Get the dimensions of the image
    image_height, image_width, _ = image.shape

    # Flatten the image pixel values to a 1D array
    image_pixels = image.flatten()

    # Get the total number of pixels in the image
    total_pixels = len(image_pixels)

    # Calculate the number of frames required to embed the entire image
    frames_needed = int(np.ceil(total_pixels / 3))  # Each pixel requires 3 frames (R, G, B)

    # Define a flag to indicate when the embedding is complete
    embedding_complete = False

    # Counter to keep track of embedded pixel index
    embedded_pixel_index = 0

    # Define the output video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 30, (640, 480))  # Adjust frame size if needed

    # Embedding process
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Extract R, G, B channels from the current frame
        R, G, B = cv2.split(frame)

        # Embed pixel values into the least significant bits of the channels
        for i in range(3):
            if embedded_pixel_index < total_pixels:
                if i == 0:
                    R = np.where(R % 2 == 0, R + 1, R) if image_pixels[embedded_pixel_index] else np.where(R % 2 != 0, R - 1, R)
                elif i == 1:
                    G = np.where(G % 2 == 0, G + 1, G) if image_pixels[embedded_pixel_index] else np.where(G % 2 != 0, G - 1, G)
                else:
                    B = np.where(B % 2 == 0, B + 1, B) if image_pixels[embedded_pixel_index] else np.where(B % 2 != 0, B - 1, B)
                embedded_pixel_index += 1
            else:
                embedding_complete = True
                break

        # Merge the R, G, B channels to form the frame
        modified_frame = cv2.merge((R, G, B))

        # Write the modified frame
        out.write(modified_frame)

        frame_count += 1

        if embedding_complete:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return frame_count

def extract_image(video_path, output_image_path, frame_count, image_height, image_width):
    # Read the video
    cap = cv2.VideoCapture(video_path)

    # Initialize an empty list to store extracted pixel values
    extracted_pixels = []

    # Counter to keep track of extracted pixel index
    extracted_pixel_index = 0

    # Extraction process
    while cap.isOpened() and extracted_pixel_index < frame_count * 3:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract R, G, B channels from the current frame
        R, G, B = cv2.split(frame)

        # Extract pixel values from the least significant bits of the channels
        for i in range(3):
            if extracted_pixel_index < frame_count * 3:
                if i == 0:
                    extracted_pixels.append(R[0, 0] % 2)
                elif i == 1:
                    extracted_pixels.append(G[0, 0] % 2)
                else:
                    extracted_pixels.append(B[0, 0] % 2)
                extracted_pixel_index += 1

    # Convert the extracted pixels list to a numpy array
    extracted_pixels_array = np.array(extracted_pixels)

    # Reshape the extracted pixels array to match the original image dimensions
    extracted_image_pixels = extracted_pixels_array[:frame_count * 3].reshape((-1, 3))

    # Convert the extracted pixels array to uint8 datatype
    extracted_image_pixels = extracted_image_pixels.astype(np.uint8)

    # Reshape the extracted pixels array to the original image shape
    extracted_image = extracted_image_pixels.reshape((image_height, image_width, 3))

    # Write the extracted image to file
    cv2.imwrite(output_image_path, extracted_image)

if __name__ == "__main__":
    video_path = 'input_video.mp4'  # Replace with your input video file path
    image_path = 'image_to_embed.png'  # Replace with your image to embed
    output_video_path = 'output_video_with_embedded_image.mp4'  # Output video path
    output_image_path = 'extracted_image.png'  # Output image path

    # Embed the image into the video
    frame_count = embed_image(video_path, image_path)
    print("Image embedded successfully.")

    # Extract the image from the video
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape
    extract_image(video_path, output_image_path, frame_count, image_height, image_width)
    print("Image extracted successfully.")
