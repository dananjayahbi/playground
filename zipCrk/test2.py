import zipfile
import binascii

def extract_zip_metadata(zip_file_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zf:
        # Access the first file in the ZIP archive (you can adjust this if needed)
        zip_info = zf.infolist()[0]

        # Extract the CRC32 checksum from the metadata
        crc32_checksum = zip_info.CRC

        # Extract the encrypted file data as bytes
        encrypted_data = zf.read(zip_info.filename)

        print(f"File name: {zip_info.filename}")
        print(f"CRC32 checksum: {crc32_checksum:#010x}")  # Display CRC32 in hexadecimal format
        print(f"Encrypted data length: {len(encrypted_data)} bytes")

        return crc32_checksum, encrypted_data

if __name__ == "__main__":
    zip_file_path = input("Enter the path to the zip file: ")
    crc32_checksum, encrypted_data = extract_zip_metadata(zip_file_path)

    # You can now pass crc32_checksum and encrypted_data to GPU-based processing
