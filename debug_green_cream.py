"""Debug script to test Green Cream selection for different sizes."""

from playwright.sync_api import sync_playwright
import time

url = "https://www.ebay.co.uk/itm/363486576357"

def test_variant(size, color):
    print(f"\n{'='*80}")
    print(f"Testing: SIZE={size}, COLOR={color}")
    print(f"{'='*80}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1366, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )
        page = context.new_page()
        
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)
        
        # Find variant containers
        containers = page.locator("div.vim.x-sku")
        print(f"\nFound {containers.count()} variant containers")
        
        # Select SIZE
        size_container = containers.nth(0)
        size_button = size_container.locator("button.listbox-button__control").first
        size_button.click()
        page.wait_for_timeout(300)
        
        # Find size options
        options_container = size_container.locator("div.listbox__options").first
        size_options = options_container.locator("div.listbox__option")
        
        print(f"\nSize options found: {size_options.count()}")
        
        # Select the size
        for idx in range(size_options.count()):
            opt = size_options.nth(idx)
            text = opt.inner_text().strip()
            if size.lower() in text.lower():
                print(f"  Selecting size: {text}")
                opt.click()
                page.wait_for_timeout(800)
                break
        
        # Wait for page to update
        try:
            page.wait_for_load_state("networkidle", timeout=3000)
        except:
            pass
        page.wait_for_timeout(1000)
        
        # Select COLOR
        color_container = containers.nth(1)
        color_button = color_container.locator("button.listbox-button__control").first
        color_button.click()
        page.wait_for_timeout(300)
        
        # Find color options
        color_options_container = color_container.locator("div.listbox__options").first
        color_options = color_options_container.locator("div.listbox__option")
        
        print(f"\nColor options found: {color_options.count()}")
        
        # Search for Green Cream
        found = False
        for idx in range(color_options.count()):
            opt = color_options.nth(idx)
            text = opt.inner_text().strip()
            data_sku = opt.get_attribute("data-sku-value-name")
            class_attr = opt.get_attribute("class")
            aria_disabled = opt.get_attribute("aria-disabled")
            
            if color.lower() in text.lower():
                print(f"\n  Option {idx}:")
                print(f"    Text: {text}")
                print(f"    data-sku-value-name: {data_sku}")
                print(f"    class: {class_attr}")
                print(f"    aria-disabled: {aria_disabled}")
                
                # Check if disabled
                is_disabled = False
                if class_attr and "listbox__option--disabled" in class_attr:
                    is_disabled = True
                    print(f"    ✗ DISABLED (class)")
                if aria_disabled == "true":
                    is_disabled = True
                    print(f"    ✗ DISABLED (aria-disabled)")
                if "(out of stock)" in text.lower():
                    is_disabled = True
                    print(f"    ✗ DISABLED (text contains 'out of stock')")
                
                if not is_disabled:
                    print(f"    ✓ AVAILABLE")
                    try:
                        opt.click()
                        page.wait_for_timeout(1000)
                        print(f"    ✓ Successfully clicked")
                    except Exception as e:
                        print(f"    ✗ Failed to click: {e}")
                else:
                    print(f"    ✗ Cannot click - option is disabled")
                
                found = True
                break
        
        if not found:
            print(f"\n  ✗ '{color}' not found in color options")
        
        # Keep browser open for inspection
        print(f"\nBrowser will stay open for 10 seconds for inspection...")
        page.wait_for_timeout(10000)
        
        browser.close()

if __name__ == "__main__":
    # Test both sizes
    test_variant("40 x 60 cm", "Green Cream")
    test_variant("60 x 110 cm", "Green Cream")
