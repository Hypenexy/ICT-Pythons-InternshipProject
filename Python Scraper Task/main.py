import os
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

website_choice = input("Choose which website to scrape (number): ")