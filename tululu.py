import argparse, logging, os, time
import pickle, requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.error import HTTPError
from urllib.parse import urljoin


def check_for_redirect(book_page):
    if book_page.history:
        raise requests.exceptions.HTTPError


def make_soup(book_id):
    try:
        url = f'https://tululu.org/b{book_id}/'
        book_page = requests.get(url)
        book_page.raise_for_status()
        soup = BeautifulSoup(book_page.text, 'lxml')

        return soup

    except:
        raise requests.exceptions.HTTPError


def get_book_link_credentials(soup):

    book_credentials = []

    book_title_author = soup.select_one('div.bookimage a')['title']
    author_title_split = book_title_author.split(' - ')
    author = author_title_split[0]
    title = ' '.join(author_title_split[1:])

    book_pic_link = soup.select_one('div.bookimage img')['src']
    book_pic_link = urljoin('https://tululu.org/shots', book_pic_link)

    book_download_link = soup.select('table.d_book a')[8].get('href')
    book_download_link = urljoin('https://tululu.org/txt.php', book_download_link)

    book_credentials.append(book_download_link)
    book_credentials.append(title)
    book_credentials.append(book_pic_link)
    book_credentials.append(author)

    return book_credentials


def download_txt(url, filename, folder='books/'):
    try:
        book_page = requests.get(url, allow_redirects=False)
        book_page.raise_for_status()
        check_for_redirect(book_page)

        filename = sanitize_filename(filename)

        with open(f"{os.path.join(folder, filename)}", 'wb') as file:
            file.write(book_page.content)

    except requests.exceptions.HTTPError:
        raise requests.exceptions.HTTPError


def download_book_cover(filename, book_cover_url, folder='books/'):
    try:
        book_cover = requests.get(book_cover_url, allow_redirects=False)
        book_cover.raise_for_status()
        check_for_redirect(book_cover)

        filename = sanitize_filename(filename)

        with open(f"{os.path.join(folder, filename)}.jpg", 'wb') as file:
            file.write(book_cover.content)
    except:
        raise requests.exceptions.HTTPError


def get_comments(soup):

    all_comments = []
    comments = soup.select('span.black')
    all_comments = [comment.text for comment in comments]

    return all_comments


def get_genre(soup):

    genre = soup.select_one('span.d_book a')['title']
    genre_split = genre.split(' - ')
    genre_split.pop()

    return genre_split


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
        try:
            soup = make_soup(book_id)
            url, filename, book_cover_url, author = get_book_link_credentials(soup)

            if filename not in books_titles:
                books_titles.append(filename)

            else:
                filename = f"{filename}_{book_id}"
                books_titles.append(filename)
            
            download_txt(url, filename)
            download_book_cover(filename, book_cover_url)

            all_comments = get_comments(soup)
            genre = get_genre(soup)

            book_additional = {
                "Название книги: ": filename,
                "Автор: ": author,
                "Жанр: ": genre,
                "Комментарии: ": all_comments,
                }

            with open(f'{os.path.join(folder, filename)}_additional.txt', 'wb') as file:
                pickle.dump(book_additional, file)

        except requests.exceptions.ConnectionError:
            logging.exception('Connection issues, will retry after timeout.')
            time.sleep(30)
        except requests.exceptions.HTTPError:
            print('HTTP Error, broken link or redirect')
        except TypeError:
            print(f'Unable to make soup for book {book_id} due to insufficient data')
        except IndexError:
            print(f'Unable to download book {book_id} due to missing link')


if __name__ == '__main__':
    main()