from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextBoxHorizontal, LTTextLineHorizontal, LTChar
import re

pattern = re.compile(r"[sS]\.\s.*?(?:\n.*?)*?\d+\s?[A-Z]?(?:\.(?:\n|$)|\n|$)")

def extract_font_size(text_line):
    # Calculate the average font size in a line
    font_sizes = [char.size for char in text_line if isinstance(char, LTChar)]
    return sum(font_sizes) / len(font_sizes) if font_sizes else None


def detect_page_margins(pdf_path):
    min_x0 = float('inf')
    max_x1 = float('-inf')
    min_y0 = float('inf')
    max_y1 = float('-inf')

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        x0, y0, x1, y1 = text_line.bbox

                        # Update the minimum and maximum coordinates
                        min_x0 = min(min_x0, x0)
                        max_x1 = max(max_x1, x1)
                        min_y0 = min(min_y0, y0)
                        max_y1 = max(max_y1, y1)

    # Return the detected content area margins
    return {
        'left_margin': min_x0,
        'right_margin': max_x1,
        'top_margin': max_y1,
        'bottom_margin': min_y0
    }


def extract_business_descriptions_with_tabs(pdf_path):
    descriptions = []
    current_description = []
    left_margin = detect_page_margins(pdf_path)['left_margin']

    for page_layout in extract_pages(pdf_path):
        for element in page_layout:
            if isinstance(element, LTTextBoxHorizontal):
                for text_line in element:
                    if isinstance(text_line, LTTextLineHorizontal):
                        x0, _, _, _ = text_line.bbox

                        # Extract font size to determine tab threshold
                        font_size = extract_font_size(text_line)
                        if font_size:
                            tab_threshold = font_size * 1.5  # Adjust this multiplier as needed
                        else:
                            tab_threshold = 20  # Default if font size is not available

                        text = text_line.get_text().strip()

                        # Check if it's a new section or a header based on `x0` and tab threshold
                        if x0 < left_margin + tab_threshold:
                            # New section; save the current description if any
                            if current_description:
                                description_text = " ".join(current_description)

                                if pattern.search(description_text):
                                    descriptions.append(description_text)
                            current_description = [text]
                        elif x0 > 110:
                            # Header, skip it
                            continue
                        else:
                            # Part of the current section
                            current_description.append(text)

    # Add the last description if any
    if current_description:
        description_text = " ".join(current_description)
        if pattern.search(description_text):
            descriptions.append(description_text)

    return descriptions


# Assuming detect_page_margins is already defined
pdf_path = "sources/page5withczur.pdf"
descriptions = extract_business_descriptions_with_tabs(pdf_path)

# Print the extracted descriptions
for desc in descriptions:
    print(desc)
    print("\n")
