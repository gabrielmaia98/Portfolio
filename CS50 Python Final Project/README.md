# Set50

This is my CS50P's Final Project documentation and rant.

#### Video Demo: https://www.youtube.com/watch?v=QDn_sMehuvM

#### Note:

This is a long text about this project, it is not meant to be a simple and straighfoward 500 words documentation, I didn't try to be objective or succint, I actually wanted to write my personal considerations about this whole thing, as probably no one will read it but myself. If anyone actually ends up reading it, I hope it is not boring. If you are from the CS50 staff, the most confusing part of the code is the scraping, and it will be throughly explained here. If you want details on the implementation, you may scroll until you see code.

### Description:

set50 is a command that sets your directory structure when taking a CS50 course. It automatically creates a course and weeks folders and downloads lecture's source code and assignment's files for each week. Its core functionality is built upon three main functions: ```handle_user_input()```, ```set50()``` and ```scrape_files_names```. The later will scrape the course urls and get the data that will then be used by the first to set up the directory structure.

Originally, I planned to have the scraping done in a different file, store the course data in a .txt, and then run only set50 on project.py. I actually started implementing it like that, and it worked fine, but I changed my mind and decided to go for a "smaller" approach with only one file. However, it was my first time scraping a website and using BeautifulSoup, so I failed to proper modularize my scraping code, and decided to simply get things done quickly, as I currently lack the time to finish it as I would like to. I also wanted to add more visual features from rich, such as progress bars, a directory tree output, and maybe other stuff, but currently I find myself lacking the time and the motivation to learn the intricacies of another library and refactor all the code that, even though is messy, is also functional enough to me. I also tried to use as many type hints as possible, but I didn't feel like working with argparse and BeautifulSoup custom types, so part of it is lacking.

This whole situation, later, became a great lesson on the importance of best practices, and got me thinking on reading the MIT software construction book. Had I accounted for those things better, I would probably be able to refactor the code, add new features, and maintain it better. Maybe one day, more skilled and mature, I will come back to this and give back the CS50 community something actually good.

#### Disclaimer:

If you are not already familiar with the Terminal, this tool is not for you. A good reason for the CS50 team to not have implemented this already is that is it a good practice for beginners to learn common commands like `cd`, `mkdir`, etc. I'm making this code available for those who already know how to use those tools and just want to have this all set up and ready to go. You also should use it at your own risk. I assume no responsability for whatever use you make of this code.

#### Currently, the following courses are supported:

- [CS50x](https://cs50.harvard.edu/x/)
- [CS50 Python](https://cs50.harvard.edu/python/)
- [CS50 R](https://cs50.harvard.edu/r/)
- [CS50 SQL](https://cs50.harvard.edu/sql/)

## Usage:

Either:

```bash
$ python3 project.py course -flags?
```

or

```bash
$ set50 course -flags
```

After I figure out how to compile it.

Note that in both approaches you shouldn't type the course name as ```CS50course```, but simply as ```course```. So it should be  ```set50 x``` or ```python project.py x```.

#### Flags:

```bash
-h / --help
-q / --quiet
-v / --verbose (default)
-d / --delete
-nsc / --no-source-code
```

The verbose approach is the default one, as I had some trouble finding a good set of colors for the outputs and I want this work to be seen. \
The delete flag will, as the name suggests, delete an already existing folder with the course name. \
The no source code flag will not download the weeks lecture's source code, as some may see this fiting.

#### Usage example:

```bash
$ set50 python
```
This will setup a directory structure simmilar to the following

    CS50 Python/
    ├── 00 Functions, Variables/
    │   ├── pset/
    │   │   ├── einstein/
    │   │   │   └── einstein.py
    │   │   ├── faces/
    │   │   │   └── faces.py
    │   │   ├── indoor/
    │   │   │   └── indoor.py
    │   │   ├── playback/
    │   │   │   └── playback.py
    │   │   └── tip/
    │   │       └── tip.py
    │   └── src0/
    │   .   ├── calculator0.py
    │   .   ├── calculator1.py
    │   .   ├── calculator2.py
    │   .   ├── calculator3.py
    │   .   ├── calculator4.py
    .   .   .
    .   .   .
    .   .   .
    ├── 01 Conditionals/
    │   ├── pset/
    │   │   ├── bank/
    │   │   │   └── bank.py
    │   │   ├── deep/
    │   │   │   └── deep.py
    │   │   ├── extensions/
    │   │   │   └── extensions.py
    │   │   ├── interpreter/
    │   │   │   └── interpreter.py
    │   │   └── meal/
    │   │       └── meal.py
    │   └── src1/
    │   .   ├── agree0.py
    │   .   ├── agree1.py
    │   .   ├── agree2.py
    │   .   ├── agree3.py
    .   .   .
    .   .   .
    .   .   .

If the no source code flag is chosen, the src folders and their files won't be included.

## Project Structure

    set50/
    │
    ├── project.py            # Scrapes the data and creates the directory structure
    ├── test_project.py       # Unit tests for some functions
    ├── requirements.txt      # List of required dependencies
    ├── README.md             # Project documentation
    └── LICENSE               # Licensing (GPL 3.0)

### Dependencies

```python
import argparse
from rich_argparse import RawDescriptionRichHelpFormatter
from rich.console import Console
from rich.prompt import Confirm
import re
import os
import sys
import wget
import zipfile
import requests
from bs4 import BeautifulSoup
import shutil
```

### project.py

As said in the project's description, at its core, project.py has three main functions, called inside its main():
- handle_user_input()
- set50()
- scrape_files_names()

#### Main:

The main function was originally inteded to only call the other functions, as the rest were not supposed to deal with side effects (printing). However, I came to found myself prioritizing functionality and user experience later, so you may see some

```python
if not quiet:
    console.print("...")
```

inside of it.

The functions that are called in main will be explained here not in the order they appear, but as I see fit for a better understanding of the project, specially for beginners such as myself.

#### Handle User Input:

That's the first function that is called inside main, it is built with regular argparse features, such as parser.add_argument() and parser.add_mutually_exclusive_group(). The former being used for parsing most arguments and the later being used to not accept conflict between the flags --quiet and --verbose. Most of it I learned only reading Python's official argparse tutorial/how to[^1].

The function then returns a tuple composed of:
- args.CS50,
- args.quiet,
- args.delete, and
- args.nosourcecode.

This tuple will then be unpacked inside main as course, quiet, delete, and nsc and further passed as arguments to the other functions. I believe their meaning to be pretty easy to catch, so let's move on.

Most of them just give us boolean values, as they are parsed with the action="store_true" argument, but args.CS50 returns us a string, telling the choosen course. And to make it easier to parse the arguments, I have defined the args.CS50 argument as the following:

```python
parser.add_argument("CS50", help="the course you want to take: x, Python, R, SQL",
                    choices=["x", "Python", "R", "SQL"], type=case_validation)
```

The choices keyword takes a list of the accepted arguments, so I don't have to worry with this kind of validation. However, I also accounted for letter casing with the custom function case_validation, passed as an argument for type. If you took CS50 Python as up until 2025, you may recall that the type keyword defines the type of the argument that is expected, so, for instance, providing int as an argument will convert the input to an integer. However, type also takes built-in and user defined functions[^2].

A different feature of the argument parsing is the use of the custom formarter class RawDescriptionRichHelpFormatter as an argument for argparse.ArgumentParser's formater class:

```python
parser = argparse.ArgumentParser(prog='Set50', formatter_class=RawDescriptionRichHelpFormatter,...
```

It is imported from [rich-argparse](https://github.com/hamdanal/rich-argparse), a package available on pip that was made to combine rich's printing with argparse. I found it while googling ways to use rich[^3].

#### Case Validation:

```python
def case_validation(value: str) -> str:
```

That's a pretty simple function, used only within the partsing. It takes and returns a string as argument. It converts the user input to a value that will be accepted by the rest of the code using regular str methods, such as str.lower, str.title and str.upper. I kept it as simple as I could.

To be more concrete, if a user types `python project.py X`, he will still get the desired outcome, because of case_validation, that will make it to be processed as `python project.py x` instead.

#### remove_course()

This is one of the first functions you may see in the source code, as it may first be called in main, if the delete argument is set to True. Not much to it, it just deletes any directory with the name of the course under the current directory. 

The cool thing here is rich's confirm class[^4], from the prompt module.

#### Scrape Files Names:

```python
def scrape_files_names(course: str, quiet: bool, nsc: bool) -> list[str]:
```

Inside main, once the input is handled, it is then passed to scrape_files_names() as a string within a try except blocked. Lots of things could go wrong with this function, but I choose to focus on errors associated with requests[^5], because I throughly tested and debuged it, and the only thing I didn't remember accounting for was a bad internet connection. Silly mistake. I didn't want to risk refactoring the code, so I just put that there, but I would prefer a cleaner approach.

Other tan the course, it also takes quiet and nsc as arguments. Quiet is the argument that tells if the script should or should not produce outputs, there's not much to it. nsc is described elsewhere as the one that tells if it should or should not download the source code of the lectures. I actually don't believe downloading it is really helpful, I just wanted to have this feature so the directory tree may look beautiful in this readme file. Anyway, the described functionality is a white lie, the actual use of nsc is to tell scrape_files_names() if it should or should not append the source code files' urls to the list that will then be returned and passed to set_50().

By the begining of scrape_files_names(), the following lists are defined:

```python
lista: list[str] = []
files: list[str] = []  # actually the folders
links: list[str] = []
psets_folders: list[str] = []
psets_urls: list[str] = []
```

This also showcases how I was learning while doing, I could probably have be more economical here, and choose a better name for "files".

Within the loops of this function, those lists are then filled with scraped info and urls from the cs50 webpages. They are later, by the end of the function, combined in a single list:

```python
lista.extend(files)
if not nsc:
    lista.extend(links)
lista.extend(psets)
lista.extend(psets_folders)
lista.extend(psets_urls)
return lista
```

This is the basically how this function works. When considering this project, I asked ChatGPT about how I could store the data and it told me I could use dictionaries or some OOP approach, but not lists, as far as I remember. I tried thinking of a way to make this work with dictionaries to maybe store this in a JSON file, but I couldn't come up with anything, so I decided to do it this way (that I came up with myself, it's not great, but I'm proud of figuring things out by myself). I then asked ChatGPT to explain me how this could work with dictionaries, and the solution was awesome, his approach for reading the data and then executing it was much more elegant than mine. That's further motivation to study Data Structures and Algorithms. If anyone from the CS50 staff reads this, I want to make it clear that I didn't use any lines of code or answers from AI agents.

So, this function is messy this way because it started as a simple exploration, but I kept going further and further, untill I've had so much work I didn't want to throw it out. Yep, **I fell for the sunk cost fallacy**.

Anyway, it starts as a regular web scraping with BeautifulSoup, requesting a page and then making the soup, etc. etc. Soon, however, I noticed that in CS50x I was not getting the course's weeks' titles. This was probably one of the first poor solutions, but **I decided to split the function between scraping either for CS50x or for the other courses with an if-else statement**. This is on the first identation level of the function:

```python
def scrape_files_names(course: str, quiet: bool, nsc: bool) -> list[str]:
...
...
...
    if course == 'CS50x':
...
...
...
    else:
...
```

All of the scraping will be made within this block. And within it, one of the consequences (and reasons) of not properly modularizing the code as functions, is that it will be repeated too often. And this is the case. So, to not make this documentation also repetitive, I will explain only the scrapping for CS50x, as the rest is based on it with few modifications. I will also briefly explain the problem I've had with the next_siblings method, that made the code even bigger within the else block.

So, as set_50 will read this list in order and I didn't wanted to bother having to sort it later, I started by appending the root directory of our couse:

```python
files.append(course + "/")
```
##### Please note that I have called get_course before. The reason I wanted the course's name to be the other way was for using it on the url.

Then, I call the soup.find_all() method to find all list itens, knowing among those I will find each course week. I've had trouble with this method, because I was not sure how to use a bs4.ResultSet, so I had to explore with it before figuring this out. Soon, after playing and googling[^6], I realized it was just a sort of list that I could iterate over and get some bs4.Tag.

```python
for item in soup.find_all('ul'):
    for element in item.find_all('li'):
        if "Week" in element.text:
            new_file = course + "/" + element.text + "/"
            files.append(new_file)
```

Then, when dealing with the list items, I've had one of the first differences for getting the weeks. In CS50x, I could take advantage of the "Week" text everywhere, in the others I've had to use other methods, that are now hard to understand for the lack of proper variables and variable names. Anyway, after getting the week name, a new file is added to the folders list.

Then, on the same level of identation, another soup is created for scraping that week's source code link. Note that on the html, most of CS50 links are relative (not actual urls), this is the reason why some of the code related to urls and folders is the way it is. In the following case, element.a.attrs\['href'], gives us the week's number.

```python
            new_url = url + element.a.attrs['href']
            new_soup = BeautifulSoup(requests.get(new_url).content, 'lxml')
```

In a simmilar fashion, more nested loops are called to scrape within that week's url and get the source code url.

```python
            # get source code urls
            for some in new_soup.find_all('ul'):
                for someth in some.find_all('li'):
                    for something in someth.find_all('a'):
                        if "Zip" in something.text:
                            src_url = something.attrs['href']
            links.append(new_file + "_:_" + src_url)
```

The \_:_ is used to help a function identify this as link and to have its root folder, so I can just call str.split within set_50.

This way I already had the weeks' folders and the source code for each lectures' code. Now I needed to get psets folders, files and links. Getting the psets' folders was easy, as they were to be a simple folder nested under the week folder. Here I simply did this, later in the code:

```python
psets = [x + "pset/" for x in files if x != (course + "/")]
```

We were already 5 for loops nested, but nothing is too bad it can't get worse, so I went to scrape the pset folders. To do this, I simply replaced the updated url, so instead of cs50.harvard.edu/{course}/year/weeks, I would have cs50.harvard.edu/{course}/year/psets.

```python
        # pset folders
    pset_url = new_url.replace("weeks", "psets")
    pset_soup = BeautifulSoup(requests.get(pset_url).content, 'lxml')
```

And then we are back looking for psets folders. When scraping, I noticed I could go direct for all the a tags, and get rid of the ones that didn't fit me. This is the reason of the if else block. There's probably a more pythonic way to write this than an "if pass", but this will do it for now.

```python
    for thing in pset_soup.find_all('a', href=True):
        if thing['href'].startswith("http") or thing['href'].startswith("..") or thing['href'].startswith("mail"):
            pass
        else:
            pset_folder = new_file + 'pset/' + thing['href']
            psets_folders.append(pset_folder)
```

Now, the following code is dedicated to find psets files, such as hello.py and urls. I'm not going to explain it throughly, just look for the if statements to get a hold of what I'm looking for in each place, and how I'm looking for it.

```python
        coisa_soup = BeautifulSoup(requests.get(
            pset_url + thing['href']).content, 'lxml')
        for coisa in coisa_soup.find_all('li'):
            if 'a file called' in coisa.text:
                psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
        for coisa in coisa_soup.find_all('p'):
            if 'a file called' in coisa.text:
                psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
            elif 'a filed called' in coisa.text:
                psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
        for coisa in coisa_soup.find_all('code'):
            if 'code' in coisa.text:
                if '<link' in coisa.text:
                    pass
                else:
                    psets_urls.append(
                        pset_folder + coisa.text.replace("code ", "").strip("\n"))
            elif 'wget' in coisa.text:
                if element.text != '4':
                    psets_urls.append(
                        new_file + "pset/" + "_:_" + coisa.text.replace("wget ", "").strip("\n"))
                else:
                    psets_urls.append(pset_folder + "_:_" +
                                        coisa.text.replace("wget ", "").strip("\n"))

```

Now, this is basically it, but I said I would explain a problem I've had with the next_siblings method. When scrapping for the other courses, I inteded to use it to iterate over all the folders, but, for whatever reason, it didn't iterate over the first one. So, the code under the the first else block will always first get the first item of the lists and then iterate over the elements of the soup to get the other items. It is unnecessarily long and complicated, and I won't go over it.

#### set_50()

Really no mystery here, it will take a list os strings, pass each one of them through auxiliary functions and either create a folder, a file, or download, unzip and delete the zip of the file.

```python
def set_50(files: list[str], quiet: bool) -> None:
    for item in files:
        if is_folder(item):
            if not quiet:
                console.print(f"[bold blue]Creating folder:[/bold blue] {item}")
            os.makedirs(item)
        elif is_file(item):
            if not quiet:
                console.print(f"[bold green]Creating file:[/bold green] {item}")
            open(item, "w")
        elif is_link(item):
            path, url = item.split("_:_")
            if not quiet:
                console.print(f"[bold khaki1]Downloading:[/bold khaki1] {url}")
            wget.download(url, path, bar=None)
            if ".zip" in url:
                with zipfile.ZipFile(path + "/" + os.path.basename(url), 'r') as zip_f:
                    zip_f.extractall(os.path.dirname(path))
                    if not quiet:
                        console.print(f"[bold]Unzipping:[/bold] {os.path.basename(url)}")
                os.remove(path + "/" + os.path.basename(url))
```

#### is_something() functions

A serie of functions you may see in set_50(). Their only purpose it to correctly validate each item passed to set_50. They were adequately tested in test_project.py.

#### fix functions

Well, even though I brute force the results already in the scrape function, I found it to still be lacking some details I would like, so I made those functions to fine tune things.

### Bye

Too tired for more, I won't even proofread this. So long, and thanks for all the Python.

[^1]: https://docs.python.org/3/howto/argparse.html
[^2]: https://docs.python.org/3/library/argparse.html#type
[^3]: https://rich.readthedocs.io/en/stable/prompt.html
[^4]: https://github.com/Textualize/rich/discussions/2258#discussioncomment-3543128
[^5]: https://www.tutorialspoint.com/exception-handling-of-python-requests-module
[^6]: https://tedboy.github.io/bs4_doc/generated/generated/bs4.ResultSet.html
