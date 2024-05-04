import pywt
import wave
import numpy as np
import pygame

def wavelet_transform(audio_file):
    with wave.open(audio_file, 'rb') as f:
        # Read the audio data
        audio_data = f.readframes(f.getnframes())
        audio_array = np.frombuffer(audio_data, dtype=np.int16)

        # Perform wavelet decomposition
        wavelet = 'bior6.8'  # Choose a wavelet
        coeffs = pywt.wavedec(audio_array, wavelet, level=1)  # Decompose the signal to one level

        # Extract approximation and detail coefficients
        cA, cD = coeffs

        # Reconstruct the signal
        recon_signal = pywt.waverec((cA, cD), wavelet)

    return recon_signal, cA, cD, f.getparams()

def encrypt_message(message):
    key = 3  # Replace with your desired key for encryption
    encrypted_message = ""
    for char in message:
        new_char = chr(ord(char) + key)
        encrypted_message += new_char

    return encrypted_message

def embed_message(signal, message):
    # Convert the message to a binary string
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    # Convert the signal to an array of integers
    signal_int = np.array(signal, dtype=np.int16)

    # Embed the binary message into the least significant bits of the signal
    for i in range(len(binary_message)):
        signal_int[i] &= 0b11111110  # Clear the least significant bit
        signal_int[i] |= int(binary_message[i])

    # Convert the signal back to the original data type
    embedded_signal = np.array(signal_int, dtype=signal.dtype)

    return embedded_signal

def play_audio(file_path, message):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    print(f"\nPlaying {message}...")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def extract_message(embedded_signal, num_bits):
    # Convert the embedded signal to an array of integers
    embedded_signal_int = np.array(embedded_signal, dtype=np.int16)

    # Extract the least significant bits from each integer to get the binary message
    extracted_bits = embedded_signal_int & 1

    # Convert the extracted bits to a binary string
    binary_message = ''.join(str(bit) for bit in extracted_bits[:num_bits])

    # Convert the binary string to characters
    extracted_message = ''.join(chr(int(binary_message[i:i+8], 2)) for i in range(0, len(binary_message), 8))

    return extracted_message

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
    audio_file = 'sample.wav'  # Replace with your audio file path

    # Get message from user and encrypt it
    user_message = input("Enter the message to encrypt and embed: ")
    encrypted_message = encrypt_message(user_message)

    print(f"Encrypted message: {encrypted_message}")

    # Perform the first wavelet transform
    recon_signal1, cA1, cD1, params = wavelet_transform(audio_file)

    # Perform a second wavelet transform on the lower-frequency part (cA1)
    recon_signal2, cA2, cD2, _ = wavelet_transform(audio_file)

    # Embed the encrypted message into the second reconstructed signal
    embedded_signal = embed_message(recon_signal2, encrypted_message)

    # Save the embedded signal
    with wave.Wave_write('embedded_signal.wav') as wave_output:
        wave_output.setparams(params)
        wave_output.writeframes(embedded_signal.astype(np.int16).tobytes())
    print("Embedded signal saved.")

    play_audio(audio_file, 'Original Signal')

    # Play the embedded signal using pygame
    play_audio('embedded_signal.wav', 'Embedded Signal')

    # Extract the embedded message from the modified signal
    extracted_message = extract_message(embedded_signal, len(encrypted_message) * 8)
    print(f"Extracted encrypted message: {extracted_message}")

    # Decrypt the extracted message
    decrypted_message = decrypt_message(extracted_message)
    print(f"Decrypted message: {decrypted_message}")
