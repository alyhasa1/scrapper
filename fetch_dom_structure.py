from playwright.sync_api import sync_playwright
import time

def fetch_ebay_dom_structure():
    url = "https://www.ebay.co.uk/itm/363486576357"
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        
        # Wait for the page to load completely
        print("Waiting for page to load completely...")
        time.sleep(3)
        
        # Try to find Size dropdown
        print("\n=== Looking for Size dropdown ===")
        size_selectors = [
            'select[aria-label*="Size"]',
            'select[name*="size"]',
            'div:has-text("Size:")',
            '[data-testid*="size"]',
            'select.x-msku__select-box',
            'select[id*="msku"]'
        ]
        
        size_html = None
        size_selector_used = None
        for selector in size_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    size_html = element.evaluate('el => el.outerHTML')
                    size_selector_used = selector
                    print(f"Found with selector: {selector}")
                    break
            except:
                continue
        
        # Try to find Colour dropdown
        print("\n=== Looking for Colour dropdown ===")
        colour_selectors = [
            'select[aria-label*="Colour"]',
            'select[aria-label*="Color"]',
            'select[name*="colour"]',
            'select[name*="color"]',
            'div:has-text("Colour:")',
            '[data-testid*="colour"]',
            '[data-testid*="color"]',
            'select.x-msku__select-box',
        ]
        
        colour_html = None
        colour_selector_used = None
        for selector in colour_selectors:
            try:
                element = page.query_selector(selector)
                if element:
                    colour_html = element.evaluate('el => el.outerHTML')
                    colour_selector_used = selector
                    print(f"Found with selector: {selector}")
                    break
            except:
                continue
        
        # Try to find all select boxes
        print("\n=== Looking for all select boxes ===")
        all_selects = page.query_selector_all('select')
        all_selects_html = []
        for i, select in enumerate(all_selects):
            try:
                html = select.evaluate('el => el.outerHTML')
                all_selects_html.append((i, html))
                print(f"Found select box {i+1}")
            except:
                continue
        
        # Try to find variation containers
        print("\n=== Looking for variation containers ===")
        variation_containers = page.query_selector_all('.x-msku__box-cont, [class*="variation"], [class*="msku"]')
        variation_html = []
        for i, container in enumerate(variation_containers):
            try:
                html = container.evaluate('el => el.outerHTML')
                variation_html.append((i, html))
                print(f"Found variation container {i+1}")
            except:
                continue
        
        # Get full page HTML as backup
        print("\n=== Getting full page HTML ===")
        full_html = page.content()
        
        browser.close()
        
        return {
            'size_html': size_html,
            'size_selector': size_selector_used,
            'colour_html': colour_html,
            'colour_selector': colour_selector_used,
            'all_selects': all_selects_html,
            'variation_containers': variation_html,
            'full_html': full_html
        }

def save_dom_analysis(data):
    output_file = "d:\\stock check scrapper\\dom_structure_analysis.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EBAY DOM STRUCTURE ANALYSIS\n")
        f.write("URL: https://www.ebay.co.uk/itm/363486576357\n")
        f.write("=" * 80 + "\n\n")
        
        # Size Dropdown Section
        f.write("=" * 80 + "\n")
        f.write("SIZE DROPDOWN SECTION\n")
        f.write("=" * 80 + "\n")
        if data['size_html']:
            f.write(f"Selector used: {data['size_selector']}\n\n")
            f.write(data['size_html'])
            f.write("\n\n")
        else:
            f.write("Size dropdown not found with standard selectors.\n\n")
        
        # Colour Dropdown Section
        f.write("=" * 80 + "\n")
        f.write("COLOUR DROPDOWN SECTION\n")
        f.write("=" * 80 + "\n")
        if data['colour_html']:
            f.write(f"Selector used: {data['colour_selector']}\n\n")
            f.write(data['colour_html'])
            f.write("\n\n")
        else:
            f.write("Colour dropdown not found with standard selectors.\n\n")
        
        # All Select Boxes Section
        f.write("=" * 80 + "\n")
        f.write("ALL SELECT BOXES FOUND ON PAGE\n")
        f.write("=" * 80 + "\n")
        if data['all_selects']:
            for i, html in data['all_selects']:
                f.write(f"\n--- SELECT BOX #{i+1} ---\n")
                f.write(html)
                f.write("\n\n")
        else:
            f.write("No select boxes found.\n\n")
        
        # Variation Containers Section
        f.write("=" * 80 + "\n")
        f.write("VARIATION CONTAINERS\n")
        f.write("=" * 80 + "\n")
        if data['variation_containers']:
            for i, html in data['variation_containers']:
                f.write(f"\n--- VARIATION CONTAINER #{i+1} ---\n")
                f.write(html[:2000])  # Limit to first 2000 chars to keep file manageable
                if len(html) > 2000:
                    f.write("\n... (truncated)")
                f.write("\n\n")
        else:
            f.write("No variation containers found.\n\n")
        
        # Key patterns to look for
        f.write("=" * 80 + "\n")
        f.write("KEY PATTERNS TO LOOK FOR\n")
        f.write("=" * 80 + "\n")
        f.write("1. Class names: Look for 'x-msku', 'variation', 'select-box'\n")
        f.write("2. Data attributes: Look for data-testid, aria-*, role attributes\n")
        f.write("3. Disabled items: Check for 'disabled' attribute, 'aria-disabled', or specific classes\n")
        f.write("4. Option structure: Check if using <select>/<option> or custom dropdowns\n\n")
        
        # Save a portion of full HTML for reference
        f.write("=" * 80 + "\n")
        f.write("FULL PAGE HTML SAMPLE (First 50,000 characters)\n")
        f.write("=" * 80 + "\n")
        f.write(data['full_html'][:50000])
        if len(data['full_html']) > 50000:
            f.write("\n\n... (truncated for readability)")
    
    print(f"\nDOM structure analysis saved to: {output_file}")

if __name__ == "__main__":
    print("Starting eBay DOM structure fetch...\n")
    data = fetch_ebay_dom_structure()
    save_dom_analysis(data)
    print("\nDone!")
