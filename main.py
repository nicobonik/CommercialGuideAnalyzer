from pdfminer.high_level import extract_text
import re

text = extract_text("sources/page5withczur.pdf")


# text = text.replace("\n", " ").strip()

print(text)

pattern = r"[sS]\.\s.*?(?:\n.*?)*?\d+\s?[A-Z]?(?:\.(?:\n|$)|\n|$)"

# Find all matches in the text
matches = re.finditer(pattern, text)

for match in matches:
    # Extract the matched address segment
    address_segment = match.group(0).replace("\n", " ").strip()
    print(f"Found: {address_segment}")
