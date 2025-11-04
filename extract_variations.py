from playwright.sync_api import sync_playwright
import json

def extract_variation_details():
    url = "https://www.ebay.co.uk/itm/363486576357"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Navigating to {url}...")
        page.goto(url, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(3000)
        
        # Find the variation container
        variation_container = page.query_selector('[data-testid="x-msku-evo"]')
        
        results = {}
        
        if variation_container:
            # Get full HTML of the variation container
            full_html = variation_container.evaluate('el => el.outerHTML')
            results['full_variation_html'] = full_html
            
            # Find all listbox buttons (Size, Colour, etc.)
            listbox_buttons = variation_container.query_selector_all('.listbox-button')
            
            results['variations'] = []
            
            for idx, button in enumerate(listbox_buttons):
                variation_data = {}
                
                # Get the button label (Size:, Colour:, etc.)
                label = button.evaluate('''el => {
                    const labelEl = el.querySelector('.btn__label');
                    return labelEl ? labelEl.textContent.trim() : '';
                }''')
                variation_data['label'] = label
                
                # Get current selected value
                current_value = button.evaluate('''el => {
                    const textEl = el.querySelector('.btn__text');
                    return textEl ? textEl.textContent.trim() : '';
                }''')
                variation_data['current_value'] = current_value
                
                # Get all options from the listbox
                options_container = button.query_selector('.listbox__options')
                if options_container:
                    options = options_container.query_selector_all('.listbox__option')
                    variation_data['options'] = []
                    
                    for opt in options:
                        option_info = opt.evaluate('''el => {
                            const valueEl = el.querySelector('.listbox__value');
                            const value = valueEl ? valueEl.textContent.replace('selected', '').trim() : '';
                            
                            const descEl = el.querySelector('.listbox__description, .x-sku-description');
                            const description = descEl ? descEl.textContent.trim() : '';
                            
                            const isActive = el.classList.contains('listbox__option--active');
                            const isDisabled = el.hasAttribute('aria-disabled') && el.getAttribute('aria-disabled') === 'true';
                            const classList = Array.from(el.classList);
                            const dataSkuValue = el.getAttribute('data-sku-value-name');
                            
                            return {
                                value: value,
                                description: description,
                                is_active: isActive,
                                is_disabled: isDisabled,
                                class_list: classList,
                                data_sku_value: dataSkuValue,
                                outer_html: el.outerHTML.substring(0, 500)
                            };
                        }''')
                        variation_data['options'].append(option_info)
                
                variation_data['button_html'] = button.evaluate('el => el.outerHTML')
                results['variations'].append(variation_data)
        
        browser.close()
        return results

def save_results(data):
    output_file = "d:\\stock check scrapper\\dom_structure_analysis.txt"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EBAY VARIATION DROPDOWN ANALYSIS\n")
        f.write("URL: https://www.ebay.co.uk/itm/363486576357\n")
        f.write("=" * 80 + "\n\n")
        
        if 'variations' in data:
            for idx, variation in enumerate(data['variations']):
                f.write("=" * 80 + "\n")
                f.write(f"VARIATION #{idx + 1}: {variation['label']}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Label: {variation['label']}\n")
                f.write(f"Current Value: {variation['current_value']}\n")
                f.write(f"Number of Options: {len(variation.get('options', []))}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("OPTIONS:\n")
                f.write("-" * 80 + "\n\n")
                
                for opt_idx, option in enumerate(variation.get('options', [])):
                    f.write(f"  Option {opt_idx + 1}:\n")
                    f.write(f"    Value: {option['value']}\n")
                    f.write(f"    Description: {option['description']}\n")
                    f.write(f"    Is Active: {option['is_active']}\n")
                    f.write(f"    Is Disabled: {option['is_disabled']}\n")
                    f.write(f"    Data SKU Value: {option['data_sku_value']}\n")
                    f.write(f"    Classes: {', '.join(option['class_list'])}\n")
                    f.write(f"    HTML Sample:\n      {option['outer_html'][:300]}\n\n")
                
                f.write("-" * 80 + "\n")
                f.write("FULL BUTTON HTML:\n")
                f.write("-" * 80 + "\n")
                f.write(variation['button_html'][:2000] + "\n\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("COMPLETE VARIATION CONTAINER HTML\n")
        f.write("=" * 80 + "\n\n")
        if 'full_variation_html' in data:
            f.write(data['full_variation_html'])
        
        f.write("\n\n" + "=" * 80 + "\n")
        f.write("KEY FINDINGS - HOW TO IDENTIFY DROPDOWNS\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. CONTAINER:\n")
        f.write("   - Main container: class='x-msku-evo' with data-testid='x-msku-evo'\n\n")
        
        f.write("2. DROPDOWN STRUCTURE:\n")
        f.write("   - Each dropdown: <span class='listbox-button'>\n")
        f.write("   - Button: <button class='listbox-button__control btn btn--form'>\n")
        f.write("   - Label element: <span class='btn__label'> (e.g., 'Size:', 'Colour:')\n")
        f.write("   - Current value: <span class='btn__text'> (e.g., 'Select', '40 x 60 cm')\n\n")
        
        f.write("3. OPTIONS LIST:\n")
        f.write("   - Container: <div role='listbox' class='listbox__options'>\n")
        f.write("   - Each option: <div class='listbox__option' role='option'>\n")
        f.write("   - Option value: <span class='listbox__value'>\n")
        f.write("   - Custom data: data-sku-value-name attribute\n\n")
        
        f.write("4. OUT-OF-STOCK DETECTION:\n")
        f.write("   - Check for: aria-disabled='true' attribute\n")
        f.write("   - Check for: class='listbox__option--disabled'\n")
        f.write("   - Check description: <span class='listbox__description'> or <div class='x-sku-description'>\n\n")
        
        f.write("5. ACTIVE/SELECTED OPTION:\n")
        f.write("   - Has class: 'listbox__option--active'\n")
        f.write("   - Has attribute: aria-selected='true'\n\n")
        
    print(f"\nAnalysis saved to: {output_file}")
    
    # Also save JSON for programmatic use
    json_file = "d:\\stock check scrapper\\variation_structure.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"JSON data saved to: {json_file}")

if __name__ == "__main__":
    print("Extracting variation dropdown details...\n")
    data = extract_variation_details()
    save_results(data)
    print("\nDone!")
