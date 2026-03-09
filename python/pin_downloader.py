"""
Pinterest Board Downloader
Created: 2026-03-09
Author: Gerardo Galvan
Description: A CLI tool to download high-res images from Pinterest boards and sections.
"""

import os
import sys
import requests
from playwright.sync_api import sync_playwright
from tqdm.rich import tqdm
from urllib.parse import urljoin, urlparse

def get_high_res(url):
    for size in ["/236x/", "/474x/", "/736x/", "/564x/"]:
        if size in url:
            return url.replace(size, "/originals/")
    return url

def scrape_images_while_scrolling(page, max_scrolls=20):
    found_urls = set()
    for _ in range(max_scrolls):
        imgs = page.query_selector_all("img")
        for img in imgs:
            src = img.get_attribute("src")
            if src and "i.pinimg.com" in src:
                found_urls.add(get_high_res(src))
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(1200) # Slightly longer wait for stability
    return list(found_urls)

def download_pinterest(target_url):
    # Parse the URL to determine if it's a section or a board
    path_parts = [p for p in urlparse(target_url).path.split('/') if p]
    
    # Logic: /user/board/ (Board) vs /user/board/section/ (Section)
    is_section = len(path_parts) >= 3
    root_folder = path_parts[1].capitalize() if len(path_parts) > 1 else "Downloads"
    
    with sync_playwright() as p:
        print(f"[*] Opening: {target_url}")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(target_url)
        page.wait_for_timeout(3000)

        section_map = {}

        if is_section:
            # It's a specific section (e.g., /music/band/)
            section_name = path_parts[-1].capitalize()
            section_map[section_name] = target_url
            print(f"[*] Section detected: {section_name}")
        else:
            # It's a main board, look for sub-sections
            print("[*] Board detected, scanning for sections...")
            board_path = urlparse(target_url).path.rstrip('/')
            links = page.query_selector_all(f"a[href^='{board_path}/']")
            for link in links:
                href = link.get_attribute("href")
                full_url = urljoin("https://www.pinterest.com", href).rstrip('/')
                if full_url != target_url.rstrip('/'):
                    name = full_url.split('/')[-1].replace('-', ' ').capitalize()
                    section_map[name] = full_url
            
            if not section_map:
                section_map["Main"] = target_url

        # Process the found sections/section
        for name, url in tqdm(section_map.items(), desc="Overall Progress"):
            target_dir = os.path.join(root_folder, name)
            os.makedirs(target_dir, exist_ok=True)

            if not is_section: page.goto(url)
            
            img_urls = scrape_images_while_scrolling(page)

            for i, img_url in enumerate(tqdm(img_urls, desc=f" 📂 {name}", leave=False)):
                try:
                    res = requests.get(img_url, timeout=10)
                    if res.status_code == 200:
                        ext = img_url.split('.')[-1].split('?')[0]
                        if len(ext) > 4: ext = "jpg"
                        with open(os.path.join(target_dir, f"pin_{i:03d}.{ext}"), "wb") as f:
                            f.write(res.content)
                except:
                    continue

        browser.close()
        print(f"\n[+] Done! Images saved in './{root_folder}/'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python download.py <URL>")
        sys.exit(1)
    download_pinterest(sys.argv[1])
