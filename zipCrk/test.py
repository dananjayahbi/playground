import zipfile
import zlib
import itertools
import string
from numba import cuda
import numpy as np

def get_charset(charset_choice):
    if charset_choice == "onlu-uppercase-letters":
        return string.ascii_uppercase
    elif charset_choice == "only-lowercase-letters":
        return string.ascii_lowercase
    elif charset_choice == "only-numbers":
        return string.digits
    elif charset_choice == "uppercase-and-lowercase":
        return string.ascii_letters
    else:  # any
        return string.printable

@cuda.jit
def generate_passwords_kernel(charset, length, start_idx, passwords):
    idx = cuda.grid(1)
    if idx < passwords.shape[0]:
        password = passwords[idx]
        for i in range(length):
            password[i] = charset[(start_idx + idx // (len(charset) ** i)) % len(charset)]

def generate_passwords(charset, length, batch_size, start_idx):
    passwords = np.zeros((batch_size, length), dtype=np.int32)
    charset_np = np.array([ord(c) for c in charset], dtype=np.int32)

    threads_per_block = 256
    blocks_per_grid = (batch_size + (threads_per_block - 1)) // threads_per_block

    generate_passwords_kernel[blocks_per_grid, threads_per_block](charset_np, length, start_idx, passwords)
    cuda.synchronize()

    for password in passwords:
        yield ''.join(chr(c) for c in password if c != 0)

def brute_force_zip(zip_file, charset_choice, min_length, max_length, batch_size=1000000):
    charset = get_charset(charset_choice)
    
    for length in range(min_length, max_length + 1):
        total_passwords = len(charset) ** length
        for start_idx in range(0, total_passwords, batch_size):
            for password in generate_passwords(charset, length, batch_size, start_idx):
                print(f"Trying password: {password}")
                try:
                    with zipfile.ZipFile(zip_file, 'r') as zf:
                        # Check if "tutorial.txt" exists
                        if 'tutorial.txt' not in zf.namelist():
                            continue

                        # Get the contents of "tutorial.txt"
                        with zf.open('tutorial.txt', 'r') as f:
                            content = f.read().decode()

                        # Check if the content matches the correct password
                        if content == password:
                            print(f"Password found: {password}")
                            return True
                except (RuntimeError, zlib.error, zipfile.BadZipFile):
                    continue

    print("Password not found")
    return False

if __name__ == "__main__":
    zip_file = input("Enter the path to the zip file: ")
    min_length = int(input("Enter the minimum length of the password: "))
    max_length = int(input("Enter the maximum length of the password: "))

    print("Select a charset option:")
    print("1. Only Uppercase Letters")
    print("2. Only Lowercase Letters")
    print("3. Only Numbers")
    print("4. Uppercase and Lowercase")
    print("5. Any")

    choice = input("Enter your choice (1-5): ")

    if choice == "1":
        charset_choice = "onlu-uppercase-letters"
    elif choice == "2":
        charset_choice = "only-lowercase-letters"
    elif choice == "3":
        charset_choice = "only-numbers"
    elif choice == "4":
        charset_choice = "uppercase-and-lowercase"
    else:  # any
        charset_choice = "any"

    brute_force_zip(zip_file, charset_choice, min_length, max_length)
