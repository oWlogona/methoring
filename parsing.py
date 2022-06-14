import asyncio
import logging
import os
import threading
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)


def benchmark(fun):
    def wrapper(*args, **kwargs):
        start = time.time()
        fun(*args, *kwargs)
        end = time.time()
        print(f'TIME SPENT: {end - start} sec.')

    return wrapper


class BaseParseSite(object):
    def __init__(self):
        self.base_site_url = 'https://klike.net'
        self.base_page_url = 'https://klike.net/844-nyashnye-kotiki-milye-kartinki-30-foto.html'
        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.pictures_dir = self.base_dir + 'pictures'
        self.images_link = None

    def parsing_site(self):
        site = requests.get(self.base_page_url)
        soup = BeautifulSoup(site.text, 'lxml')
        self.images_link = [self.base_site_url + item.get('src') for item in soup.find_all('img', class_='fr-dib')]

    def clear_folder(self) -> None:
        for file in os.listdir(self.pictures_dir):
            file_path = os.path.join(self.pictures_dir, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    # logging.info(f'File {file} is deleted')
            except Exception as e:
                logging.error(f'{e}: with file: {file}')


class SynchronousParsingSite(BaseParseSite):
    # @benchmark
    def save_images(self) -> None:
        self.clear_folder()
        for count, link in enumerate(self.images_link):
            with open(f'pictures/img_{count + 1}.jpg', 'wb') as file:
                file.write(requests.get(link).content)
                # logging.info(f'File img_{count + 1}.jpg is created')

    def run(self):
        self.parsing_site()
        self.save_images()


class ThreadParsingSite(BaseParseSite):

    def __init__(self):
        super(ThreadParsingSite, self).__init__()
        self.count = 0

    def save_image(self, image):
        self.count += 1
        with open(f'pictures/img_{self.count}.jpg', 'wb') as file:
            file.write(requests.get(image).content)
            # logging.info(f'File img_{self.count}.jpg is created {threading.currentThread().name}')

    def parse_images(self, images_link_list: list) -> None:
        while True:
            if not images_link_list:
                break
            item = images_link_list.pop()
            self.save_image(item)

    # @benchmark
    def run(self):
        self.parsing_site()
        self.clear_folder()
        for i in range(1, 6):
            threading.Thread(target=self.parse_images, args=(self.images_link,), name=f'THR-{i}').start()


class AsiParsingSite(BaseParseSite):

    def __init__(self):
        super(AsiParsingSite, self).__init__()
        self.count = 0

    async def save_images(self) -> None:
        while True:
            if not self.images_link:
                break
            image = self.images_link.pop()
            self.count += 1
            with open(f'pictures/img_{self.count}.jpg', 'wb') as file:
                file.write(requests.get(image).content)
                # logging.info(f'File img_{self.count}.jpg is created')

    async def run(self):
        self.parsing_site()
        self.clear_folder()
        await asyncio.gather(self.save_images())


if __name__ == '__main__':
    start = time.time()
    SynchronousParsingSite().run()
    end = time.time()
    print(f'SynchronousParsingSite: {end - start} sec')

    start = time.time()
    ThreadParsingSite().run()
    end = time.time()
    print(f'ThreadParsingSite: {end - start} sec')

    start = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsiParsingSite().run())
    end = time.time()
    print(f'AsiParsingSite: {end - start} sec')
