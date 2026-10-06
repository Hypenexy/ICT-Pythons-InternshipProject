import os
from urllib.request import Request, urlopen
dirname = os.path.dirname(__file__)
website_list_path = os.path.join(dirname, 'websites.txt')


print("Web Scraper")


with open(website_list_path) as f:
    lines = f.read().splitlines()

n = 0
for line in lines:
    spaces = ""
    if(len(lines)>9 and n<9):
        spaces = " "
    n += 1
    print(str(n) + spaces + " 🌐 " + line)

website_choice = int(input("Choose which website to scrape (number): "))

url = lines[website_choice].strip()

req = Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)

website_content = urlopen(req)

print(website_content.read())