import cv2
import numpy as np

def encrypt_message(message):
    key = 3  # Replace with your desired key for encryption
    encrypted_message = ""
    for char in message:
        new_char = chr(ord(char) + key)
        encrypted_message += new_char

    return encrypted_message

def embed_image(video_path, image_path, message):
    # Read the video
    cap = cv2.VideoCapture(video_path)

    # Read the image to be embedded
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Convert the message to a binary string
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Embed the binary message into the least significant bits of the video frame
        for i in range(len(binary_message)):
            row = frame_count % image_height
            col = (frame_count // image_height) % image_width
            channel = frame_count % 3  # Red, Green, or Blue channel

            if channel == 0:
                pixel_value = frame[row, col, 0]
            elif channel == 1:
                pixel_value = frame[row, col, 1]
            else:
                pixel_value = frame[row, col, 2]

            # Clear the least significant bit
            pixel_value &= 0b11111110
            # Embed the bit from the binary message
            pixel_value |= int(binary_message[i])

            if channel == 0:
                frame[row, col, 0] = pixel_value
            elif channel == 1:
                frame[row, col, 1] = pixel_value
            else:
                frame[row, col, 2] = pixel_value

            frame_count += 1

        yield frame

    cap.release()

def decrypt_message(encrypted_message):
    key = 3  # Replace with the same key used for encryption
    decrypted_message = ""
    for char in encrypted_message:
        try:
            new_char = chr((ord(char) - key) % 256)
            decrypted_message += new_char
        except ValueError:
            # Handle the error (skip the character, replace it, etc.)
            pass

    return decrypted_message

if __name__ == "__main__":
    video_path = 'input_video.mp4'  # Replace with your input video file path
    image_path = 'image_to_embed.png'  # Replace with your image to embed
    user_message = input("Enter the message to encrypt and embed: ")
    encrypted_message = encrypt_message(user_message)
    print("Encrypted Message: ", encrypted_message)

    # Embed the image and encrypted message into the video
    output_video_path = 'output_video_with_embedded_image.mp4'  # Output video path
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, 30, (640, 480))  # Adjust frame size if needed

    for frame in embed_image(video_path, image_path, encrypted_message):
        out.write(frame)

    out.release()
    cv2.destroyAllWindows()

    # Decrypt the embedded message
    extracted_message = decrypt_message(encrypted_message)
    print(f"Extracted encrypted message: {extracted_message}")
