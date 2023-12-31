import argparse
import json
import logging
import os
import sys
import time
from collections import defaultdict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

from main import (BookError, download_image, download_txt, get_book_page,
                  parse_book_page)

logger = logging.getLogger(__name__)


def get_categories(response):
    soup = BeautifulSoup(response.text, 'lxml')
    books_category = defaultdict(int)
    for soup_item in soup.select('#leftnavmenu dt'):
        category = ' '.join(soup_item.select('b')[0].text.split())
        link = soup_item.select('a')[0].get('href')
        books_category[category] = link
    return books_category


def get_subcategories(response):
    soup = BeautifulSoup(response.text, 'lxml')
    subcategories = defaultdict(int)
    for soup_item in soup.select('#leftnavmenu dd a'):
        subcategory = ' '.join(soup_item.text.split())[1:].strip()
        link = soup_item.get('href')
        subcategories[subcategory] = link
    return subcategories


def get_book_ids(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_ids = [
        x.get('href').strip('/')[1:] for x in (soup.select('.bookimage a'))
    ]
    return book_ids


def save_books_description(content, folder):
    file_path = os.path.join(folder, 'content_books.json')
    with open(file_path, 'w', encoding='utf8') as file:
        json.dump(content, file, indent=4, ensure_ascii=False)


def create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=('''\
            Скрипт скачивает книги с сайта https://tululu.org/
            --------------------------------------------------
            Для скачивания необходимо указать параметры:
            --start_page - первая скачиваемая страница
            --end_page - страница до которой скачиваются книги (не включительно)
            --dest_folder — путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
            --skip_imgs — пропустить загрузку картинок
            --skip_txt — пропустить загрузку книг'''
                     )
    )

    parser.add_argument('--start_page',
                        default=700,
                        nargs='?',
                        type=int,
                        help='Введите первую скачиваемую страницу'
                        )
    parser.add_argument('--end_page',
                        default=None,
                        nargs='?',
                        type=int,
                        help="Введите последнюю скачиваемую"
                             " страницу (не включительно)"
                        )
    parser.add_argument('--dest_folder',
                        default='media/books',
                        help="Введите путь к каталогу с"
                             " результатами парсинга: картинки, книги, JSON"
                        )
    parser.add_argument('--skip_imgs',
                        default=False,
                        action='store_true',
                        help="Используйте если необходимо"
                             " пропустить загрузку картинок"
                        )
    parser.add_argument('--skip_txt',
                        default=False,
                        action='store_true',
                        help="Используйте если необходимо"
                             " пропустить загрузку книг"
                        )
    parser.add_argument('--json_path',
                        default='',
                        nargs='?',
                        help='Введите путь для сохранения'
                             ' файла JSON с метаданными книг'
                        )
    return parser


if __name__ == '__main__':
    input_category = 'Фантастика - фэнтези'
    input_subcategory = 'Научная фантастика'

    book_page_ids = []
    books_description = []

    parser = create_parser()
    args = parser.parse_args(sys.argv[1:])
    try:
        home_page = get_book_page('https://tululu.org/')
        categories = get_categories(home_page)
        subcategory_page = get_book_page(urljoin(
            'https://tululu.org/',
            categories.get(input_category)
        ))
    except requests.exceptions.ConnectionError:
        logger.warning('Не удается подключиться к серверу!'
                       ' https://tululu.org/ на данный момент недоступен!')
        sys.exit()

    subcategories = get_subcategories(subcategory_page)
    subcategory_url = subcategories.get(input_subcategory)
    path = urlparse(subcategory_url).path
    last_page = args.end_page
    if not last_page:
        try:
            subcategory_page = get_book_page(subcategory_url)
        except requests.exceptions.MissingSchema:
            print(f'Категория "{input_category}"'
                  f' или подкатегория "{input_subcategory}" - отсутствует!')
            sys.exit()
        soup = BeautifulSoup(subcategory_page.text, 'lxml')
        last_page = int(soup.select('.npage')[-1]['href'].split('/')[2]) + 1

    for page in range(args.start_page, last_page):
        try:
            subcategory_page = get_book_page(
                urljoin('https://tululu.org/',
                        f'{path}/{page}/'))
            book_page_ids = book_page_ids + get_book_ids(subcategory_page)
        except requests.exceptions.HTTPError as error:
            print(error, file=sys.stderr)
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Не удается подключиться к серверу!'
                           ' Повторное подключение через 10 секунд.')
            time.sleep(10)
            continue

    if args.dest_folder:
        os.makedirs(args.dest_folder, exist_ok=True)
        dest_folder = args.dest_folder

    for book_id in book_page_ids:
        page_url = urljoin('https://tululu.org/', f'b{book_id}/')

        try:
            book_page = get_book_page(page_url)
            soup = BeautifulSoup(book_page.text, 'lxml')
            book_poster = parse_book_page(soup, book_id)
            book_name = (f'{book_id}-я книга.'
                         f' {book_poster["book_title"]}').replace(' ', '_')
            if not args.skip_txt:
                download_txt(book_id, book_name, dest_folder)
            if not args.skip_imgs:
                download_image(book_poster['book_image_url'])
        except BookError:
            logger.warning(f'Книга #{book_id} отсутствует в библиотеке.')
            continue
        except requests.exceptions.HTTPError as error:
            print(error, file=sys.stderr)
            continue
        except requests.exceptions.ConnectionError:
            logger.warning('Не удается подключиться к серверу!'
                           ' Повторное подключение через 10 секунд.')
            time.sleep(10)
            continue

        book_description = {
            'title': book_poster['book_title'],
            'autor': book_poster['book_author'],
            'img_src': f"media/images/{sanitize_filename(book_poster['book_image_url'].split('/')[-1])}",
            'book_path': f'media/books/{book_name}.txt',
            'comments': book_poster['book_comments'],
            'genres': book_poster['book_genre'],
        }

        books_description.append(book_description)
    save_books_description(books_description, args.json_path)
