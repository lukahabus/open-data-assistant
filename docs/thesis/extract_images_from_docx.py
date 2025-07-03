from docx import Document
import os
import zipfile
from pathlib import Path


def extract_images_from_docx(docx_path, output_dir):
    """Extract all images from a docx file"""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing: {docx_path}")
    print(f"Output directory: {output_dir}")

    # Method 1: Try using python-docx
    try:
        doc = Document(docx_path)
        image_count = 0

        print("Method 1: Using python-docx...")
        for rel in doc.part.rels.values():
            if "image" in str(rel.target_ref):
                image_count += 1
                image_ext = os.path.splitext(rel.target_ref)[1]
                image_data = rel.target_part.blob
                image_filename = f"izvjestaj_image_{image_count}{image_ext}"
                image_path = os.path.join(output_dir, image_filename)

                with open(image_path, "wb") as f:
                    f.write(image_data)
                print(f"  Extracted: {image_filename}")

        if image_count > 0:
            print(f"Method 1 successful: {image_count} images extracted")
            return image_count
        else:
            print("Method 1: No images found")

    except Exception as e:
        print(f"Method 1 failed: {e}")

    # Method 2: Direct zip extraction (docx is a zip file)
    try:
        print("Method 2: Using direct zip extraction...")
        image_count = 0

        with zipfile.ZipFile(docx_path, "r") as zip_ref:
            # List all files in the zip
            file_list = zip_ref.namelist()
            print(f"  Files in docx: {len(file_list)}")

            # Look for image files
            for file_name in file_list:
                if file_name.startswith("word/media/"):
                    image_count += 1
                    # Get file extension
                    ext = os.path.splitext(file_name)[1]
                    if not ext:
                        ext = ".png"  # Default extension

                    # Extract the image
                    image_filename = f"izvjestaj_image_{image_count}{ext}"
                    image_path = os.path.join(output_dir, image_filename)

                    with zip_ref.open(file_name) as source, open(
                        image_path, "wb"
                    ) as target:
                        target.write(source.read())
                    print(f"  Extracted: {image_filename} (from {file_name})")

        if image_count > 0:
            print(f"Method 2 successful: {image_count} images extracted")
            return image_count
        else:
            print("Method 2: No images found in word/media/")

    except Exception as e:
        print(f"Method 2 failed: {e}")

    # Method 3: Look for any binary files that might be images
    try:
        print("Method 3: Looking for any binary files...")
        image_count = 0

        with zipfile.ZipFile(docx_path, "r") as zip_ref:
            for file_name in zip_ref.namelist():
                if any(
                    ext in file_name.lower()
                    for ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"]
                ):
                    image_count += 1
                    ext = os.path.splitext(file_name)[1]
                    image_filename = f"izvjestaj_image_{image_count}{ext}"
                    image_path = os.path.join(output_dir, image_filename)

                    with zip_ref.open(file_name) as source, open(
                        image_path, "wb"
                    ) as target:
                        target.write(source.read())
                    print(f"  Extracted: {image_filename} (from {file_name})")

        if image_count > 0:
            print(f"Method 3 successful: {image_count} images extracted")
            return image_count
        else:
            print("Method 3: No image files found")

    except Exception as e:
        print(f"Method 3 failed: {e}")

    print("All methods failed. No images extracted.")
    return 0


# Main execution
if __name__ == "__main__":
    # Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    docx_path = os.path.join(base_dir, "izvjestaj.docx")
    figures_dir = os.path.join(base_dir, "figures")

    # Check if file exists
    if not os.path.exists(docx_path):
        print(f"Error: {docx_path} not found!")
        exit(1)

    # Extract images
    total_images = extract_images_from_docx(docx_path, figures_dir)
    print(f"\nTotal images extracted: {total_images}")

    # List all files in figures directory
    if os.path.exists(figures_dir):
        print(f"\nFiles in {figures_dir}:")
        for file in os.listdir(figures_dir):
            file_path = os.path.join(figures_dir, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                print(f"  {file} ({size} bytes)")
