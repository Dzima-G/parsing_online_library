# Парсер книг с сайта tululu.org

Набор скриптов предназначен для загрузки книг из электронной библиотеки tululu.org и создание веб-сайта.
Опубликованная версия веб-сайта, созданная в результате использования
скриптов: https://dzima-g.github.io/parsing_online_library/pages/index1.html

## Как установить

Python3 должен быть уже установлен.
Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:

```sh
pip install -r requirements.txt
```

## Как скачать книги из библиотеки

Есть два сценария. Скрипт с именем main.py может загружать книги и обложки по диапазону их идентификаторов. Скрипт
parse_tululu_category.py может загружать книги из определенной категории (раздел «Фантастика»).

Скрипты работают из консольной утилиты.

### Скрипт main.py:

Каждая книга в электронной библиотеке `tululu.org` идентифицируется по идентификатору. Скрипт принимает два аргумента:
начальный идентификатор и конечный идентификатор, чтобы установить диапазон книг, которые необходимо
загрузить. По умолчанию скрипт скачивает книги с идентификаторами от `1` до `10` (включительно). Скрипт создает
папку `media`,
в корне репозитория. Книги загружаются в папку `books` (`/media/books`), а обложки книг в
папку `images` (`/media/images`).

Для запуска скрипта без аргументов:

```sh
 python main.py 
 ```

Для указания интервала скачивания книг используются два аргумента:

`--start_id` - начало интервала (первая скачиваемая книга)

`--end_id` - конец интервала (последняя скачиваемая книга включительно)

Для запуска скрипта с аргументами:

```sh
 python main.py --start_id 1 --end_id 10
 ```

### Скрипт parse_tululu_category.py:

Этот скрипт также создает папку `media`  и папки для книг `books` и для обложек книг `images`, если это необходимо и
зависит от аргументов. Так же создает файл JSON со всеми метаданными каждой книги.

Имеет следующие аргументы:

`--start_page` - первая скачиваемая страница (по умолчанию `700`)

`--end_page` - страница до которой скачиваются книги, не включительно (по умолчанию последняя страница в подкатегории)

`--dest_folder` — путь к каталогу с результатами парсинга. (по умолчанию `/media/` )

`--skip_imgs` — пропустить загрузку картинок

`--skip_txt` — пропустить загрузку книг

`--json_path` - путь для сохранения файла JSON с метаданными книг (по умолчанию корневой каталог репозитория)

Для запуска скрипта с аргументами:

```sh
 python parse_tululu_category.py --start_page 1 --end_page 5 
 ```

## Как создать веб сайт из скачанных книг

### Скрипт render_website.py:

Создает сайт из скачанных книг скрипта `parse_tululu_category.py` используя пути к файлам по умолчанию.

Для запуска скрипта необязательный аргумент:

`--json_path` - путь к файлу content_books.json сформированного скриптом `parse_tululu_category.py` (по умолчанию
корневой каталог репозитория)

Для запуска скрипта:

```sh
 python render_website.py
 ```
После запуска скрипта сформированные страницы сайта располагаются в корне репозитория в папке `/pages`.

Что бы открыть сайт используйте один из способов:

 * Откройте браузер и введите в адресную строку этот URL http://127.0.0.1:5500/pages/index1.html

 * Откройте в папке `/pages` в корне репозитория страницу сайта, например `/pages/index1.html`.

### Цель проекта

Этот проект создан для учебных целей.
