import argparse
import os
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser()

help = """
The URL to the deck you wish to download.
Specifically, a cardgamebase link.
You can check out a list of available (for example) commander decks here:
https://cardgamebase.com/commander/
"""

parser.add_argument('url', help=help)
parser.add_argument('--dir', "-d", help="The directory to which the cards will be saved. Defaults to the name of the deck.", default=None, nargs="?")

def main():
    args = parser.parse_args()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',

    }   
    main_card_page = requests.get(url=args.url, headers=headers)
    if main_card_page.status_code == 200:
        print("We got the content from " + args.url )
    soup = BeautifulSoup(main_card_page.content, "html.parser")
    
    results = soup.find_all('a', href=True, class_="deckbox_link")
    for row in results:
        if row:
            
            card_page = requests.get(url=row['href'], headers=headers)
            if card_page.status_code != 200:
                print("ERROR: The card's page returned: " + card_page.status_code)
                continue
            soup = BeautifulSoup(card_page.content, 'html.parser')
            image_result = soup.find(id="card_image")
            src = image_result['src']
            if src:
                image = requests.get(url=src).content
                path = urlparse(src)
                # we strip /cardgamebase.com from the url as to get the deck name itself
                # unsure whether every single deck uses the same URL structure
                dir_name = args.url.split('/cardgamebase.com', 1)[-1].lstrip('/')
                dir_full = os.path.join(os.curdir, dir_name)
                output_dir = args.dir or dir_full
                if not os.path.isdir(output_dir):
                    print("Card directory not found, creating at: " + os.path.abspath(output_dir))
                    os.mkdir(output_dir)
                if not os.path.isfile(f"{output_dir}/{os.path.basename(path.path)}"):
                    with open(f"{output_dir}/{os.path.basename(path.path)}", 'wb') as f:
                        f.write(image)
                else:
                    print("File found, skipping...")
            else:
                print(f"WARNING: source for {image_result} not found!")

                


            

main()