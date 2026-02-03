import re

def format_text(text: str) -> str:
    if not text or not text.strip():
        return "No answer generated."

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line = line.rstrip()
        line = re.sub(r'[ \t]{2,}', ' ', line)

        cleaned_lines.append(line)

    formatted = "\n".join(cleaned_lines).strip()

    return formatted


