#!/usr/bin/env python3
"""
Script to compile LaTeX diagrams into PNG images.
"""

import os
import subprocess
import sys


def compile_diagram(tex_file, output_dir="figures"):
    """Compile a LaTeX diagram to PNG."""
    try:
        # Get the base name without extension
        base_name = os.path.splitext(os.path.basename(tex_file))[0]

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Compile using pdflatex
        print(f"Compiling {tex_file}...")
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory=" + output_dir,
                tex_file,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"Error compiling {tex_file}:")
            print(result.stderr)
            return False

        # Convert PDF to PNG using ImageMagick
        pdf_file = os.path.join(output_dir, base_name + ".pdf")
        png_file = os.path.join(output_dir, base_name + ".png")

        if os.path.exists(pdf_file):
            print(f"Converting {pdf_file} to PNG...")
            result = subprocess.run(
                ["magick", "-density", "300", pdf_file, "-quality", "100", png_file],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"Successfully created {png_file}")
                return True
            else:
                print(f"Error converting to PNG: {result.stderr}")
                return False
        else:
            print(f"PDF file {pdf_file} not found")
            return False

    except Exception as e:
        print(f"Error processing {tex_file}: {e}")
        return False


def main():
    """Main function to compile all diagrams."""
    # List of diagram files to compile
    diagrams = [
        "system_architecture.tex",
        "rag_pipeline.tex",
        "multimodal_search.tex",
        "schema_extraction.tex",
        "validation_error_handling.tex",
        "system_architecture_detailed.tex",
    ]

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(script_dir, "figures")

    success_count = 0
    total_count = len(diagrams)

    for diagram in diagrams:
        tex_file = os.path.join(figures_dir, diagram)
        if os.path.exists(tex_file):
            if compile_diagram(tex_file, figures_dir):
                success_count += 1
        else:
            print(f"File {tex_file} not found")

    print(
        f"\nCompilation complete: {success_count}/{total_count} diagrams compiled successfully"
    )

    if success_count < total_count:
        print("\nTo compile manually, you can use:")
        print("1. pdflatex -interaction=nonstopmode diagram.tex")
        print("2. magick -density 300 diagram.pdf -quality 100 diagram.png")
        print("\nMake sure you have LaTeX and ImageMagick installed.")


if __name__ == "__main__":
    main()
