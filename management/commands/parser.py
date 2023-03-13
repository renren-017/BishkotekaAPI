import asyncio
import aiohttp
import aiofiles
import openpyxl
import requests
import re
from bs4 import BeautifulSoup
from openpyxl import Workbook
from django.core.management.base import BaseCommand, CommandError

BASE_URL = 'https://armenianbd.com'


async def download_image(session, url, filename):
    async with session.get(url) as response:
        async with aiofiles.open(filename, 'wb') as f:
            async for chunk in response.content.iter_chunked(1024):
                await f.write(chunk)


async def scrape_link(session, url, n, ws):
    try:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            content_block = soup.find('div', class_='content').find('div', class_='cont_block').find('div', class_='news-main')
            title = content_block.find('h2', class_='news-inner-title').text.strip()
            date = content_block.find('span', class_='news-inner-date').text.strip()
            image_url = BASE_URL + content_block.find('img', class_='news-inner-image').get('src')
            image_filename = f'static/img/news_photos/image_{"_".join(title.split()[:3])}.jpg'
            await download_image(session, image_url, image_filename)
            body = soup.find('div', {'class': 'news-inner-body'}).prettify().replace('<br>', '').replace('</br>', '').replace('<br/>', '')
            ws.append([title, date, body, image_filename, url])
    except Exception as e:
        print(e)


async def get_links_on_page(session, page_url):
    links = []
    async with session.get(page_url) as response:
        print(page_url)
        soup = BeautifulSoup(await response.text(), 'html.parser')
        news_blocks = soup.select('.news-cat-view .news-block')
        for block in news_blocks:
            image = block.select_one('a')
            if image:
                link = BASE_URL + image.get('href')
                links.append(link)

        page_url = [*page_url]
        if not page_url[-6] == '0':
            page_url[-6] = str(int(page_url[-6]) + 1)
            next_page_link = "".join(page_url)
            return links, next_page_link

        return links, None


async def main(link):
    async with aiohttp.ClientSession() as session:
        page_url = BASE_URL + link
        links = []
        next_page_link = page_url

        while next_page_link:
            page_links, next_page_link = await get_links_on_page(session, next_page_link)
            links += page_links

        wb = Workbook()
        ws = wb.active
        ws.append(['Title', 'Date', 'Body', 'Image', 'Link'])

        tasks = []
        for n, url in enumerate(links, start=1):
            task = asyncio.create_task(scrape_link(session, url, n, ws))
            tasks.append(task)

        await asyncio.gather(*tasks)
        wb.save('forarmenians_app/management/commands/news.xlsx')


class Command(BaseCommand):
    help = 'Parses news to an xlsx file'

    def add_arguments(self, parser):
        parser.add_argument('link', type=str)

    def handle(self, *args, **options):
        asyncio.run(main(options['link']))
