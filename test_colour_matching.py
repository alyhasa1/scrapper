def extract_base_colour(colour_text):
    text = colour_text.strip()
    
    # Handle "GelBack-Pink" format (prefix-colour) -> extract "pink"
    if text.lower().startswith('gelback-') or text.lower().startswith('gel back-'):
        parts = text.split('-', 1)
        if len(parts) == 2:
            return parts[1].strip().lower()
    
    # Handle "Pink - Gel Back 59" format (colour - suffix) -> extract "pink"
    if ' - ' in text:
        base = text.split(' - ')[0].strip()
        return base.lower()
    
    # Handle "GelBack Pink" format (prefix space colour) -> extract "pink"
    if text.lower().startswith('gelback ') or text.lower().startswith('gel back '):
        parts = text.split(' ', 1)
        if len(parts) == 2:
            return parts[1].strip().lower()
    
    return text.lower()

tests = [
    ('GelBack-Pink', 'Pink - Gel Back 59'),
    ('GelBack-Beige', 'Beige - Gel Back 59'),
    ('GelBack-Ochre', 'Ochre - Gel Back 59'),
    ('GelBack-Blue', 'Blue - Gel Back 59'),
]

for excel, ebay in tests:
    excel_base = extract_base_colour(excel)
    ebay_base = extract_base_colour(ebay)
    match = excel_base == ebay_base
    print(f"{excel:20} -> {excel_base:15} | {ebay:25} -> {ebay_base:15} | Match: {match}")
