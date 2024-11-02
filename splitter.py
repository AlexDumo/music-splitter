import argparse
import yaml
import PyPDF2
import os
from pathlib import Path


def split_pdf(dir: Path):
    yaml_file = next(dir.glob("*.yaml"), None)
    if yaml_file is None:
        print(
            f"No YAML file found in the directory '{str(dir)}'."
            + "\nDid you copy the part_template.yaml into the correct place?"
        )
        return
    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file)

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

            output_path = dir / f"{i} - {piece_name} - {part['name']}.pdf"
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
    args = parser.parse_args()
    if(args.dir.is_dir()):
        split_pdf(args.dir)
    else:
        print(f"Directory '{args.dir}' does not exist.")
        exit(1)
