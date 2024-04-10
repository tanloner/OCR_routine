# Text Extraction from Images and PDFs

This project is a Python application that extracts text from images and PDFs. It uses libraries such as pytesseract, pillow, and pdf2image to perform the extraction.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need to have Python installed on your machine. You can download it from the official website: https://www.python.org/downloads/

### Installing

1. Navigate to the project directory
```bash
cd Jojo_OCR
```
2. Install the required packages
```bash
pip install -r requirements.txt
```
3. Adjust the config.json file to suit your needs.

## Usage

The application continuously scans the 'Documents' directory for any new images or PDFs. If it finds any, it extracts the text from them and writes it to an 'output.txt' file in the same directory.

To run the application, use the following command:
```bash
python main.py
```
## Contributing

Go ahead and contribute to this project if you feel like it needs improvement.

## License
This project is licensed under the MIT License - see the LICENSE.md file for details