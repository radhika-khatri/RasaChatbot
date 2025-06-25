# model_utils.py

import os
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sentence_transformers import SentenceTransformer, util

BASE_URL = "https://xtributor.com/US"
SIMILARITY_THRESHOLD = 0.4
BLOCKS_PER_PAGE = 8

model = SentenceTransformer('all-MiniLM-L6-v2')

def html_to_structured_json_by_blocks(html_content, blocks_per_page=BLOCKS_PER_PAGE):
    soup = BeautifulSoup(html_content, "html.parser")
    body = soup.body or soup
    sections = []

    current_section = {"page": 1, "text": "", "images": []}
    block_count = 0

    for elem in body.descendants:
        if not hasattr(elem, "name"):
            continue

        if elem.name == "p":
            current_section["text"] += elem.get_text(strip=True) + "\n"
            block_count += 1

        elif elem.name == "ul":
            for li in elem.find_all("li"):
                current_section["text"] += "• " + li.get_text(strip=True) + "\n"
            block_count += 1

        elif elem.name == "img":
            src = elem.get("src")
            if src:
                current_section["images"].append(src)
                block_count += 1

        if block_count >= blocks_per_page:
            sections.append(current_section)
            current_section = {"page": len(sections) + 1, "text": "", "images": []}
            block_count = 0

    if current_section["text"].strip() or current_section["images"]:
        sections.append(current_section)

    return sections


def extract_all_steps_if_any_match(text, query, threshold=SIMILARITY_THRESHOLD):
    lines = [s.strip() for s in text.strip().split('\n') if s.strip()]
    query_embedding = model.encode(query, convert_to_tensor=True)
    step_pattern = re.compile(r"(?i)^(•\s*)?step\s*\d+[:.]|•\s*\d+[.:]")
    matching_steps = []

    for i, line in enumerate(lines):
        if step_pattern.match(line):
            line_embedding = model.encode(line, convert_to_tensor=True)
            score = util.pytorch_cos_sim(query_embedding, line_embedding).item()
            if score > threshold:
                matching_steps.append(i)

    if not matching_steps:
        return []

    return [line for line in lines if step_pattern.match(line)]


def extract_relevant_lines(text, query, threshold=SIMILARITY_THRESHOLD):
    lines = [s.strip() for s in text.strip().split('\n') if s.strip()]
    query_embedding = model.encode(query, convert_to_tensor=True)
    relevant_lines = []

    for line in lines:
        line_embedding = model.encode(line, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, line_embedding).item()
        if score > threshold:
            relevant_lines.append(line)

    return relevant_lines


def generate_response_from_structured_json(query, structured_data):
    query_embedding = model.encode(query, convert_to_tensor=True)
    seen_texts = set()
    seen_images = set()
    combined_sentences = []
    images = []

    for chunk in structured_data:
        text = chunk.get("text", "").strip()
        if not text or text in seen_texts:
            continue

        text_embedding = model.encode(text, convert_to_tensor=True)
        score = util.pytorch_cos_sim(query_embedding, text_embedding).item()

        if score > SIMILARITY_THRESHOLD:
            relevant_sentences = extract_all_steps_if_any_match(text, query)
            if not relevant_sentences:
                relevant_sentences = extract_relevant_lines(text, query)

            if relevant_sentences:
                combined_sentences.extend(relevant_sentences)
                seen_texts.add(text)

            for img_url in chunk.get("images", []):
                full_url = urljoin(BASE_URL, img_url)
                if full_url not in seen_images:
                    images.append(full_url)
                    seen_images.add(full_url)

    return format_response(combined_sentences), images


def format_response(sentences):
    formatted = ""
    for line in sentences:
        if re.match(r"(?i)^step\s*\d+[:.]", line):
            formatted += f"✅ {line}\n\n"
        elif re.match(r"•\s*\d+[.:]", line) or re.match(r"(?i)^(•\s*)?step\s*\d+[:.]", line):
            formatted += f"🔸 {line}\n\n"
        elif line.lower().startswith("note"):
            formatted += f"📝 {line}\n\n"
        else:
            formatted += f"{line}\n\n"
    return formatted.strip()
