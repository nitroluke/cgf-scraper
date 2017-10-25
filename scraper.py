#!/usr/bin/env python

import requests
from pprint import PrettyPrinter
from bs4 import BeautifulSoup
from re import search

FILE_REGEX = "(file=)(.*?)(&)"
YOUTUBE_ID_REGEX = "(=)(.*?)(&)"

IFRAME_PREFIX = "\"<iframe width=\"560\" height=\"315\" src=\""

IFRAME_POSTFIX = "\" frameborder=\"0\" allowfullscreen></iframe>\""
YOUTUBE_EMBED= "https://www.youtube.com/embed/"
CGF_ADDRESS = "http://cgfnw.org/"
DOWNLOAD_FILE_PREFIX = CGF_ADDRESS + "download.php?file="


def main():
    page = requests.get("http://cgfnw.org/media.php?page=1&ipp=All&&type=1")
    soup = BeautifulSoup(page.content, 'html.parser')
    rows = soup.find_all("tr")
    row_data = []
    for row in rows[1:]:
        info = {}
        columns = row.find_all('td')
        info['date'] = columns[0].next.strip("\n\t")
        info['speaker'] = columns[1].next.strip("\n\t")
        if columns[2]:
            title = columns[2].find('h1')
            if title:
                info['title'] = title.next
            process_links(columns[2], info)
        row_data.append(info)

    f = open("boss_sauce.txt", 'w+')
    pprint = PrettyPrinter(1, 120, stream=f)
    pprint.pprint(row_data)
    f.close()


def process_links(link_column, info):
    clean_links = []
    for aTag in link_column.find_all('a'):
        link = aTag.get('href')
        if link and len(link) > 1:
            link = link.replace("\r", '')
            link = link.replace("\t", '')
            link = link.replace("\n", '')
            file = clean_file_match(search(FILE_REGEX, link))
            if file:
                full_link = CGF_ADDRESS + file
                if full_link not in clean_links:
                    clean_links.append(CGF_ADDRESS + file)
                    clean_links.append(DOWNLOAD_FILE_PREFIX + file)
                else:
                    print("found duplicates?")
            else:
                youtube_id = clean_youtube_id(search(YOUTUBE_ID_REGEX, link))
                if youtube_id:
                    info['iframe'] = IFRAME_PREFIX + YOUTUBE_EMBED + link + IFRAME_POSTFIX
                else:
                    # These are sermon summaries/Pdfs
                    if "downloadlit" not in link:
                        pdf_link = DOWNLOAD_FILE_PREFIX + link
                        clean_links.append(pdf_link)
                    else:
                        misc_link = CGF_ADDRESS + link
                        clean_links.append(misc_link)
    info['links'] = clean_links


def clean_file_match(in_match):
    if in_match:
        file = in_match.group()
        # strip these off because I was too lazy to come up with a regex to match everything between these two things.
        file = file.strip('&')
        # could just use file.replace() here but *shrug*
        if file.startswith("file="):
            file = file[5:]
        return file


def clean_youtube_id(in_match):
    if in_match:
        youtube_id = in_match.group()
        youtube_id = youtube_id.strip('&')
        youtube_id = youtube_id.strip("=")
        return youtube_id

if __name__ == '__main__':
    main()