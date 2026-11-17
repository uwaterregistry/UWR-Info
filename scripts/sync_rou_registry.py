import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
BASE = "https://www.uwaterregistry.io"
LISTING = f"{BASE}/RouListing"
OUTPUT = Path("data/rou-projects.json")
HEADERS = {
    "User-Agent": "UWR-Public-Registry-Mirror/1.0 (read-only; contact info@uwaterregistry.io)"
}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)
def get_page(url):
    response = SESSION.get(url, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")
def normalise(text):
    return re.sub(r"\s+", " ", text or "").strip()
def find_listing_pages():
    """Discover listing pagination links without guessing page numbers."""
    queue = [LISTING]
    visited = set()
    project_links = {}
    while queue and len(visited) < 30:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        soup = get_page(url)
        for link in soup.find_all("a", href=True):
            label = normalise(link.get_text(" ", strip=True))
            href = urljoin(BASE, link["href"])
            parsed = urlparse(href)
            # Project cards link to individual registry detail pages.
            match = re.search(
                r"UWR ID Number:\s*(\d{3})",
                label,
                re.IGNORECASE
            )
            if match and parsed.netloc == urlparse(BASE).netloc:
                project_id = match.group(1)
                if parsed.path.lower().startswith("/registry/details"):
                    project_links[project_id] = href
            # Follow only listing pagination links.
            is_listing = parsed.path.rstrip("/").lower() == "/roulisting"
            is_page_link = (
                label.isdigit()
                or "next" in label.lower()
                or label in (">", "»", "›")
            )
            if is_listing and is_page_link and href not in visited:
                queue.append(href)
        time.sleep(0.5)
    return project_links
def lines_from(soup):
    return [
        normalise(line)
        for line in soup.get_text("\n", strip=True).splitlines()
        if normalise(line)
    ]
def value_after(lines, label):
    for index, line in enumerate(lines):
        if line.lower() == label.lower() and index + 1 < len(lines):
            return lines[index + 1]
    return None
def section_between(lines, start_label, end_labels):
    start = None
    for index, line in enumerate(lines):
        if line.lower() == start_label.lower():
            start = index + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].lower() in [x.lower() for x in end_labels]:
            end = index
            break
    return "\n".join(lines[start:end])
def parse_serial_records(text):
    pattern = re.compile(
        r"Serial Number\s+([^\n]+)\s+"
        r"Vintage Year\s+(\d{4})\s+"
        r"Status\s+([^\n]+)\s+"
        r"RoU's Available\s+([\d,]+)",
        re.IGNORECASE
    )
    records = []
    for match in pattern.finditer(text):
        records.append({
            "serial_number": match.group(1).strip(),
            "vintage_year": int(match.group(2)),
            "status": match.group(3).strip(),
            "rous_available": int(match.group(4).replace(",", ""))
        })
    return records
def parse_event_records(text, event_type):
    """
    Parse public registry entries.
    Missing or unrecognised entries are not invented.
    """
    chunks = re.split(
        r"(?m)(?=^\s*[\d,]+\s+RoU\s+\()",
        text
    )
    records = []
    for chunk in chunks:
        match = re.search(
            r"([\d,]+)\s+RoU\s+\(([^)]+)\)\s+"
            r"has been\s+(.+?)\s+on\s+([^\n]+)",
            chunk,
            re.IGNORECASE
        )
        if not match:
            continue
        record = {
            "quantity": int(match.group(1).replace(",", "")),
            "serial_number": match.group(2).strip(),
            "registry_event_text": match.group(3).strip(),
            "recorded_at": match.group(4).strip(),
            "event_type": event_type
        }
        reason = re.search(r"Reason:\s*(.+)", chunk, re.IGNORECASE)
        if reason:
            record["reason"] = reason.group(1).strip()
        token = re.search(
            r"Name of Blockchain Token:\s*(.+)",
            chunk,
            re.IGNORECASE
        )
        if token:
            record["token_name"] = token.group(1).strip()
        records.append(record)
    return records
def parse_project(project_id, detail_url):
    soup = get_page(detail_url)
    lines = lines_from(soup)
    full_text = "\n".join(lines)
    title_index = next(
        (
            i for i, line in enumerate(lines)
            if re.search(
                rf"UWR ID Number:\s*{project_id}\b",
                line,
                re.IGNORECASE
            )
        ),
        None
    )
    if title_index is None:
        raise ValueError(
            f"Project ID {project_id} not found on its detail page"
        )
    title_line = lines[title_index]
    project_name = re.sub(
        r"\s*\(UWR ID Number:\s*\d{3}\).*",
        "",
        title_line,
        flags=re.IGNORECASE
    ).strip()
    project_status = (
        lines[title_index + 1]
        if title_index + 1 < len(lines)
        else "Not stated"
    )
    description = section_between(
        lines,
        "Project Description",
        ["Project Category"]
    )
    retired_text = section_between(
        lines,
        "Retired RoU",
        ["Burnt & Tokenized RoU", "Image", "Home"]
    )
    tokenized_text = section_between(
        lines,
        "Burnt & Tokenized RoU",
        ["Image", "Home", "About Us", "Contact Us"]
    )
    serial_records = parse_serial_records(full_text)
    total_match = re.search(
        r"TOTAL Serialized RoU's.*?\n([\d,]+)",
        full_text,
        re.IGNORECASE | re.DOTALL
    )
    total_registered = (
        int(total_match.group(1).replace(",", ""))
        if total_match else None
    )
    return {
        "project_id": project_id,
        "project_name": project_name,
        "project_status": project_status,
        "project_description": description,
        "project_category": value_after(lines, "Project Category"),
        "location": value_after(lines, "Location"),
        "project_type": value_after(lines, "Type"),
        "credit_serial_records": serial_records,
        "total_registered_rous": total_registered,
        "retirement_records": parse_event_records(
            retired_text, "retired"
        ),
        "tokenisation_records": parse_event_records(
            tokenized_text, "burnt_and_tokenized"
        ),
        "registry_detail_url": detail_url
    }
def main():
    project_links = find_listing_pages()
    if not project_links:
        raise RuntimeError(
            "No project detail links found. "
            "The registry page may have changed; "
            "the previous JSON file will not be overwritten."
        )
    projects = []
    for project_id, detail_url in sorted(
        project_links.items(),
        key=lambda item: int(item[0])
    ):
        try:
            project = parse_project(project_id, detail_url)
            projects.append(project)
            print(f"Read project {project_id}: {project['project_name']}")
        except Exception as error:
            print(f"ERROR reading project {project_id}: {error}")
            raise
        time.sleep(0.5)
    if len(projects) != len(project_links):
        raise RuntimeError("Incomplete project mirror; refusing to publish.")
    result = {
        "dataset_name": "UWR Public RoU Registry Mirror",
        "dataset_type": "read_only_mirror",
        "authority": "Universal Water Registry",
        "authority_url": BASE,
        "listing_url": LISTING,
        "mirror_notice": (
            "This is an official synchronised public-data mirror."
            "The live UWR project detail page available on https://www.uwaterregistry.io/RouListing is authoritative. "
            "Always follow the source link to confirm current status."
        ),
        "generated_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "project_count": len(projects),
        "projects": projects
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    temporary.replace(OUTPUT)
    print(f"Published {len(projects)} projects to {OUTPUT}")
if __name__ == "__main__":
    main()
