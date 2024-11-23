import argparse
import yaml
import PyPDF2
import os
from pathlib import Path


def split_pdf(dir: Path, password = None):
    yaml_file = next(dir.glob("*.yaml"), None)
    if yaml_file is None:
        print(
            f"No YAML file found in the directory '{str(dir)}'."
            + "\nDid you copy the part_template.yaml into the correct place?"
        )
        return
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)
    start_index = data["start_index"] if "start_index" in data else 1

    pdf_files = [file for file in dir.glob("*.pdf")]
    if len(pdf_files) == 0:
        print(
            f"No PDF files found in the directory '{str(dir)}'."
            + "\nDid you copy the PDF file into the correct place?"
        )
        return
    elif len(pdf_files) > 1:
        print(
            f"Multiple PDF files found in the directory '{str(dir)}'."
            + "\nPlease ensure there is only one PDF file in the directory with the parts."
        )
        return
    pdf_path = pdf_files[0]
    piece_name = data["piece_name"]
    parts = data["parts"]

    with open(pdf_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)

        if password is not None and reader.is_encrypted:
            print("Decrypting pdf with provided password")
            reader.decrypt(password)
        elif password is not None:
            print("Password provided, but PDF is not encrypted. Ignoring password...")
        elif reader.is_encrypted:
            print("PDF file is encrypted. Please provide a password with the '-p' flag")
            return

        current_page = parts[0]["start_page"] - 1

        def get_start_page(part, current_page):
            if part["start_page"] < 0:
                return abs(part["start_page"]) + current_page
            else:
                return part["start_page"] - 1

        for i, part in enumerate(parts):
            writer = PyPDF2.PdfWriter()
            start_page = get_start_page(part, current_page)

            if i + 1 < len(parts):
                end_page = get_start_page(parts[i + 1], start_page)
            else:
                end_page = len(reader.pages)

            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])

            output_path = dir / f"{i + start_index} - {piece_name} - {part['name']}.pdf"
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            print(f"Created: '{output_path.name}'")
            print(f"\tPages {[i + 1 for i in range(start_page, end_page)]}")
            current_page = start_page


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split a long PDF file of brass band parts into separate PDF files."
    )
    parser.add_argument(
        "dir",
        type=Path,
        help="The directory containing the PDF file and YAML file.",
    )
    parser.add_argument('-p', '--password', help="The password to the PDF (if it has one)")
    args = parser.parse_args()
    if(args.dir.is_dir()):
        split_pdf(args.dir, password=args.password)
    else:
        print(f"Directory '{args.dir}' does not exist.")
        exit(1)
