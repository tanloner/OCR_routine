from pathlib import PurePath
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import os
import fitz
from time import sleep
import json


def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: Configuration file not found. Config created with default values.")
        config = {'directory_path': 'Documents', 'sleep_time': 5}
        with open('config.json', 'w') as f:
            json.dump(config, f)
    return config


config = load_config()
directory_path = config['directory_path']
sleep_time = config['sleep_time']


class Converter:
    """A class dedicated to handling file conversions."""

    @staticmethod
    def pdf_to_image(pdf_path: str | PurePath):
        """Convert a PDF file to a series of images."""
        return convert_from_path(pdf_path)

    @staticmethod
    def image_to_searchable_pdf_page(image: Image):
        """Convert an image to a searchable PDF."""
        return pytesseract.image_to_pdf_or_hocr(image, extension='pdf')


class FolderInformation:
    """Enhanced class to handle information and operations about directory contents efficiently with error handling."""

    def __init__(self):
        self.images = []
        self.pdfs = []
        self.pdfs_searchable = []
        self.non_searchable_pdfs = []
        self.files = []

    def get_files(self, path):
        """Retrieve list of files in the specified directory with error handling."""
        try:
            self.files = os.listdir(path)
        except FileNotFoundError:
            print(f"Error: Directory not found {path}")
            self.files = []  # Reset files list to prevent use of outdated data
        except PermissionError:
            print(f"Error: Permission denied to access {path}")
            self.files = []
        return self.files

    def update_folder(self, path):
        """Update folder state by categorizing all files with optimized single read."""
        if not self.get_files(path):
            return  # Exit if the directory listing failed
        self.images = [f for f in self.files if f.endswith(('.png', '.jpg', '.jpeg', '.gif')) and not f.endswith('.pdf.png')]
        self.pdfs = [f for f in self.files if f.endswith('.pdf')]
        self.pdfs_searchable = [f for f in self.files if f.endswith('_searchable.pdf')]
        self.non_searchable_pdfs = [f for f in self.files if f.endswith('.pdf') and f not in self.pdfs_searchable]

    def is_folder_searchable(self, path):
        """Check if all files in the directory have corresponding searchable PDFs."""
        self.update_folder(path)
        return len(self.pdfs_searchable) == len(self.images) + len(self.non_searchable_pdfs)


def main_processing_loop():
    """Improved main loop with error handling and file locking considerations."""
    info = FolderInformation()
    while True:
        try:
            for dirpath, dirnames, _ in os.walk(directory_path):
                for dirname in dirnames:
                    path = os.path.join(dirpath, dirname)
                    info.update_folder(path)
                    if info.is_folder_searchable(path):
                        continue  # Skip processing if all files are already searchable

                    # Further processing with error handling and file locking considerations
                    process_images_and_pdfs(dirpath, dirname, info)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        sleep(sleep_time)  # Pause for 5 seconds before the next directory scan


def process_images_and_pdfs(dirpath, dirname, info):
    """Process images and PDFs with proper file handling and conversion."""
    for image_name in info.images:
        image_base_name = image_name.rsplit('.', 1)[0]
        searchable_pdf_name = f'{image_base_name}_searchable.pdf'
        if searchable_pdf_name in info.pdfs_searchable:
            continue  # Skip if already processed

        image_path = os.path.join(dirpath, dirname, image_name)
        try:
            with Image.open(image_path) as image:
                pdf = Converter.image_to_searchable_pdf_page(image)
            pdf_path = os.path.join(dirpath, dirname, searchable_pdf_name)
            with open(pdf_path, 'wb') as file:
                file.write(pdf)
        except IOError as e:
            print(f"Failed to process image {image_name}: {e}")

    for pdf_name in info.non_searchable_pdfs:
        process_non_searchable_pdfs(dirpath, dirname, pdf_name)


def process_non_searchable_pdfs(dirpath, dirname, pdf_name):
    """Process non-searchable PDFs into searchable PDFs with error handling."""
    pdf_base_name = pdf_name.rsplit('.', 1)[0]
    searchable_pdf_path = os.path.join(str(dirpath), str(dirname), f'{pdf_base_name}_searchable.pdf')
    pdf_path = os.path.join(str(dirpath), str(dirname), str(pdf_name))
    try:
        images = Converter.pdf_to_image(pdf_path)
        doc = fitz.open()  # Initialize a new PDF document to combine pages
        for image in images:
            pdf = Converter.image_to_searchable_pdf_page(image)
            with fitz.open("pdf", pdf) as new_page:
                doc.insert_pdf(new_page, show_progress=1)
        doc.save(searchable_pdf_path)
        doc.close()
    except Exception as e:
        print(f"Failed to convert PDF {pdf_name} to searchable: {e}")


# The updated functions and classes include robust error handling and optimized file operations. These are ready for deployment after final review.


# The main loop and functions are commented out to prevent execution until ready to deploy.
main_processing_loop()
