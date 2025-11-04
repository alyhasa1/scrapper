from urllib import request
from bs4 import BeautifulSoup
import re
import json

url = "https://www.ebay.co.uk/itm/363486576357"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
}
req = request.Request(url, headers=headers)
with request.urlopen(req) as resp:
    html_bytes = resp.read()
html = html_bytes.decode("utf-8", errors="ignore")

with open("sample_listing.html", "wb") as fh:
    fh.write(html_bytes)

print("html len", len(html))

match = re.search(r'"itemVariationsMap":\s*(\{.*?\})\s*,\s*"seoMetadata"', html, re.S)
if not match:
    print("variations map not found via regex")
else:
    data = match.group(1)
    print("map snippet len", len(data))
    try:
        obj = json.loads('{"itemVariationsMap":' + data + '}' )
        print("parsed keys", list(obj["itemVariationsMap"].keys())[:3])
    except json.JSONDecodeError as exc:
        print("json decode error", exc)

soup = BeautifulSoup(html, "html.parser")
for script in soup.find_all("script"):
    text = script.string or script.text
    if not text:
        continue
    if "itemVariationsMap" in text:
        snippet = text.strip()
        print("script match len", len(snippet))
        print("snippet start", snippet[:400])
        break
else:
    print("no script tag with variations map")

sku_options = soup.select('.listbox__option[data-sku-value-name]')
print("found sku options", len(sku_options))
if sku_options:
    print([opt['data-sku-value-name'] for opt in sku_options[:5]])
