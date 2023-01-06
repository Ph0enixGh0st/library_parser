# Library Parser
The script downloads books and saves them to the script folder.

### How to install
Using GitHub CLI:
```bash
gh repo clone Ph0enixGh0st/library_parser
```
Or download and unpack ZIP file from GIT Hub repository: https://github.com/Ph0enixGh0st/library_parser.git

# Prerequisites
Python3 should be already installed. 
Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

# tululu.py and how to run it
The script downloads books from tululu.org and saves them to 'books' folder from where the script is run.
When running the script book text files and book cover image files will be created.

In order to start the script please run the following command in terminal/cmd/powershell:

```bash
python tululu.py -s 100 -e 150
```

'-s' argument is the book id number starting from which the script will begin to fetch the book from tululu website.

'-e' argument is the book id number to which the script will finish fetching the books from tululu website.

Thus the above stated bash command will result in script attempt to download the books from tululu.org starting from id #100 to id #150.

### Project Goals

The code is written for educational purposes on online-course for web-developers [dvmn.org](https://dvmn.org/).
