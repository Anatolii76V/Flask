import os
import argparse
import timeit
import requests
import threading
import multiprocessing
import asyncio
import aiohttp
from pathlib import Path

image_path = Path('./images')
image_path.mkdir(parents=True, exist_ok=True)


def download_image(url):
    try:
        start_time = timeit.default_timer()
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = image_path / os.path.basename(url)
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            end_time = timeit.default_timer() - start_time
            print(f'Загрузка {filename} завершена за {end_time:.2f} секунд')
        else:
            print(f'Не удалось скачать: {url} (Код состояния: {response.status_code})')
    except Exception as e:
        print(f'Ошибка при скачивании {url}: {str(e)}')


async def download_image_async(url):
    try:
        start_time = timeit.default_timer()
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    filename = image_path / os.path.basename(url)
                    with open(filename, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    end_time = timeit.default_timer() - start_time
                    print(f'Загрузка {filename} завершена за {end_time:.2f} секунд')
                else:
                    print(f'Не удалось скачать: {url} (Код состояния: {response.status})')
    except Exception as e:
        print(f'Ошибка при асинхронном скачивании {url}: {str(e)}')


def download_images_threading(urls):
    start_time = timeit.default_timer()
    threads = []
    for url in urls:
        t = threading.Thread(target=download_image, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    end_time = timeit.default_timer() - start_time
    print(f'Загрузка завершена за {end_time:.2f} секунд')


def download_images_multiprocessor(urls):
    start_time = timeit.default_timer()
    processes = []
    for url in urls:
        p = multiprocessing.Process(target=download_image, args=(url,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
    end_time = timeit.default_timer() - start_time
    print(f'Загрузка завершена за {end_time:.2f} секунд')


async def download_images_asyncio(urls):
    start_time = timeit.default_timer()
    tasks = []
    for url in urls:
        task = asyncio.ensure_future(download_image_async(url))
        tasks.append(task)

    await asyncio.gather(*tasks)

    end_time = timeit.default_timer() - start_time
    print(f'Загрузка завершена за {end_time:.2f} секунд')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Парсер изображений по URL-адресам')
    parser.add_argument('--urls', default=['https://img3.fonwall.ru/o/fc/tree-nature-grass-swamp.jpeg',
                                           'https://img3.fonwall.ru/o/bx/nature-wilderness-wildlife-zoo.jpeg'],
                        nargs='+',
                        help='Список URL-адресов для загрузки изображений')
    args = parser.parse_args()

    print(f'Загрузка {len(args.urls)} изображений - Потоки')
    download_images_threading(args.urls)

    print(f'Загрузка {len(args.urls)} изображений - Мультипроцессор')
    download_images_multiprocessor(args.urls)

    print(f'Загрузка {len(args.urls)} изображений - Асинхронный')
    asyncio.run(download_images_asyncio(args.urls))
