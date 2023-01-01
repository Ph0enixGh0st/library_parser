import argparse
import json
import os
import pickle
import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError


def check_for_redirect(response):
    if response.status_code == 302:
        raise requests.exceptions.HTTPError


def get_download_link_and_title(book_id):
    try:
        id = book_id
        url = f'https://tululu.org/b{id}/'
        book_page = requests.get(url)

        check_for_redirect(book_page)

        soup = BeautifulSoup(book_page.text, 'lxml')
        book_title_author = soup.select_one('div.bookimage a')['title']

        author_title_split = book_title_author.split(' - ')

        author = author_title_split[0]
        title = author_title_split[1]

        book_pic_link = soup.select_one('div.bookimage img')['src']
        book_pic_link = f"https://tululu.org{book_pic_link}"

        book_download_link = soup.select('table.d_book a')[8].get('href')
        book_download_link = f"https://tululu.org{book_download_link}"

        return book_download_link, title, book_pic_link, author, title

    except:
        return False


def download_txt(url, filename, book_cover_url, folder='books/'):

    try:
        book_page = requests.get(url, allow_redirects=False)
        book_page.raise_for_status()
        check_for_redirect(book_page)

        book_cover = requests.get(book_cover_url, allow_redirects=False)
        book_cover.raise_for_status()
        check_for_redirect(book_cover)

        from pathvalidate import sanitize_filename
        filename = sanitize_filename(filename)

        with open(f"{os.path.join(folder, filename)}", 'wb') as file:
            file.write(book_page.content)

        try:
            with open(f"{os.path.join(folder, filename)}.jpg", 'wb') as file:
                file.write(book_cover.content)
        except:
            print("No book cover found")

    except requests.exceptions.HTTPError as error:
        print("Couldn't download the book")


def get_comments(id):

    all_comments = []
    try:
        url = f'https://tululu.org/b{id}/'
        book_page = requests.get(url)

        soup = BeautifulSoup(book_page.text, 'lxml')
        comments = soup.select('span.black')
        for comment in comments:
            all_comments.append(comment.text)
        return all_comments
    except:
        print('When getting book comments something has glitched')


def get_genre(id):
    try:
        url = f'https://tululu.org/b{id}/'
        book_page = requests.get(url)

        soup = BeautifulSoup(book_page.text, 'lxml')
        genre = soup.select_one('span.d_book a')['title']
        genre_split = genre.split(' - ')
        genre = genre_split[0]
        return genre
    except:
        print('When getting book genre something has glitched')


def main():

    folder = 'books'
    parent_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(parent_dir, folder)

    try:
        os.makedirs(path, exist_ok = True)
        print("Folder '%s' created successfully" %folder)
    except OSError as error:
        print("Folder '%s' can not be created")

    books_titles = []

    parser = argparse.ArgumentParser(description="The script downloads books from tululu portal")
    parser.add_argument("-s", "--start_id", default=1, help="Starting book id", type=int)
    parser.add_argument("-e", "--end_id", default=2, help="Ending book id", type=int)
    args = parser.parse_args()

    start_id = args.start_id
    end_id = args.end_id
    end_id = end_id + 1

    for book_id in range(start_id, end_id):

        if get_download_link_and_title(book_id):
            url, filename, book_cover_url, author, title = get_download_link_and_title(book_id)

            if filename not in books_titles:
                books_titles.append(filename)
                download_txt(url, filename, book_cover_url)
            else:
                filename = f"{filename}_{book_id}"
                books_titles.append(filename)
                download_txt(url, filename, book_cover_url)

            all_comments = get_comments(book_id)
            genre = get_genre(book_id)

            book_additional = {
                "Название книги: ": title,
                "Автор: ": author,
                "Жанр: ": genre,
                "Комментарии: ": all_comments,
                }

            with open(f'{os.path.join(folder, filename)}_additional.txt', 'wb') as file:
                pickle.dump(book_additional, file)

        else:
            print(f'Something went wrong with book id: {book_id}')


if __name__ == '__main__':
    main()