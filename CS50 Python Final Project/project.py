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

# to do:
# record video

console = Console()


def main() -> None:

    course, quiet, delete, nsc = handle_user_input()

    if delete:
        if Confirm.ask(f"[bold red]Are you sure you want to delete [bold blue]./{get_course_name(course)}[/bold blue] and all its content?[/bold red]"):
            try:
                remove_course(get_course_name(course))
                return
            except FileNotFoundError:
                console.print(
                    f"[bold yellow]No {get_course_name(course)} folder found[/bold yellow]")
                return
        else:
            return

    try:
        files: list[str] = scrape_files_names(course, quiet, nsc)
    except requests.exceptions.Timeout:
        console.print("[bold red]The request timed out.[/bold red]")
        sys.exit()
    except requests.exceptions.ConnectionError:
        console.print("[bold red]There was a connection error.[/bold red]")
        sys.exit()
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP error occurred:[/bold red] {e}")
        sys.exit()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]An error occurred:[/bold red] {e}")
        raise (e)

    if not quiet:
        console.print(
            f"\n[bold yellow]Setting up your directories for {get_course_name(course)}...[/bold yellow]")

    set_50(files, quiet)

    if course == "Python":
        fix_py()
    elif course == "x":
        fix_x()
    elif course == "SQL":
        fix_sql()

    if not quiet:
        console.print("\n[bold yellow]All set up and done.[/bold yellow]\n")

# Gets user input with argparse


def handle_user_input() -> tuple:

    parser = argparse.ArgumentParser(prog='Set50',
                                     formatter_class=RawDescriptionRichHelpFormatter,
                                     description='''set50 is a command that sets your directory structure when taking a CS50 course.
    Currently, it supports only the courses listed as positional arguments below:
    ''',
                                     epilog="Note that you should run it as set50 x, for instance, and not set50 cs50x."
                                     )
    parser.add_argument("CS50", help="the course you want to take: x, Python, R, SQL",
                        choices=["x", "Python", "R", "SQL"], type=case_validation)
    parser.add_argument("-d", "--delete", action="store_true", default=False,
                        help="If used, it will delete the chosen course's folder on the directory the script is being executed.")
    parser.add_argument("-nsc", "--nosourcecode", action="store_true", default=True,
                        help="If chosen, no lecture source code will be downloaded")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true")
    group.add_argument("-q", "--quiet", action="store_true")

    args = parser.parse_args()

    return args.CS50, args.quiet, args.delete, args.nosourcecode

# Validates user input according to options regardles of capitalization


def case_validation(value: str) -> str:
    if value.lower() == 'x':
        return value.lower()
    elif value.lower() == 'sql':
        return value.upper()
    else:
        return value.title()

# transforms x into CS50x, Python into CS50 Python, etc.


def get_course_name(course: str) -> str:
    if course == 'x':
        course = 'CS50' + course
    else:
        course = 'CS50 ' + course
    return course


def remove_course(course: str) -> None:
    shutil.rmtree(course)

# Sequence of auxiliary functions that will check the type of the file for set_50()


def is_folder(item: str) -> bool:
    return item.endswith("/")


def is_file(item: str) -> bool:
    if re.search(r".+\..+$", item) and not re.search(r"_:_https://.+$", item):
        return True
    else:  # here only for mypy reasons
        return False


def is_link(item: str) -> bool:
    if re.search(r"_:_https://.+$", item):
        return True
    else:  # here only for mypy reasons
        return False

# Function that will actually create the directory structure


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

# Iterate over course_data file and returns a list with the files names, to be processed


def scrape_files_names(course: str, quiet: bool, nsc: bool) -> list[str]:

    lista: list[str] = []
    files: list[str] = []  # actually the folders
    links: list[str] = []
    psets_folders: list[str] = []
    psets_urls: list[str] = []

    url = f"https://cs50.harvard.edu/{course.lower()}/weeks/"
    page = requests.get(url) # later used to scrape within the course
    url = page.url
    soup = BeautifulSoup(page.content, 'lxml')

    course: str = get_course_name(course)

    if not quiet:
        console.print(f"[bold yellow]Scraping data for {course}...[/bold yellow]")

    if course == 'CS50x':
        files.append(course + "/")
        # get folders names
        for item in soup.find_all('ul'):
            for element in item.find_all('li'):
                if "Week" in element.text:
                    new_file = course + "/" + element.text + "/"
                    files.append(new_file)
                    new_url = url + element.a.attrs['href']
                    new_soup = BeautifulSoup(requests.get(new_url).content, 'lxml')
                    if not quiet:
                        console.print(f"[bold blue]Scraping {element.text}[/bold blue]")
                    # get source code urls
                    for some in new_soup.find_all('ul'):
                        for someth in some.find_all('li'):
                            for something in someth.find_all('a'):
                                if "Zip" in something.text:
                                    src_url = something.attrs['href']
                    # append source code url
                    links.append(new_file + "_:_" + src_url)

                    # pset folders
                    pset_url = new_url.replace("weeks", "psets")
                    pset_soup = BeautifulSoup(requests.get(pset_url).content, 'lxml')
                    pset_links: list[str] = []
                    for thing in pset_soup.find_all('a', href=True):
                        if thing['href'].startswith("http") or thing['href'].startswith("..") or thing['href'].startswith("mail"):
                            pass
                        else:
                            pset_folder = new_file + 'pset/' + thing['href']
                            psets_folders.append(pset_folder)

                            # trying to get psets urls and files
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

        psets = [x + "pset/" for x in files if x != (course + "/")]
    else:

        # gets first folder, next_siblings was not iterating over it
        files.append(course + "/")
        new_file = course + "/" + '0' + \
            soup.ol.li.a.attrs['href'].replace("/", " ") + soup.ol.li.a.text + '/'
        if not quiet:
            console.print(
                f"[bold blue]Scraping week: {'0' + soup.ol.li.a.attrs['href'].replace('/', '')} {soup.ol.li.a.text}[/bold blue]")

        files.append(new_file)
        new_url = url + soup.ol.li.a.attrs['href']
        new_soup = BeautifulSoup(requests.get(new_url).content, 'lxml')

        # get first sourcecode url
        for some in new_soup.find_all('ul'):
            for someth in some.find_all('li'):
                for something in someth.find_all('a'):
                    if "Zip" in something.text:
                        src_url = something.attrs['href']
        # append source code url
        links.append(new_file + "_:_" + src_url)

        # gets first pset folders
        pset_url = new_url.replace("weeks", "psets")
        pset_soup = BeautifulSoup(requests.get(pset_url).content, 'lxml')
        for thing in pset_soup.find_all('a', href=True):
            if thing['href'].startswith("http") or thing['href'].startswith("..") or thing['href'].startswith("mail"):
                pass
            else:
                pset_folder = new_file + 'pset/' + thing['href']
                psets_folders.append(pset_folder)

                # trying to get first pset url
                coisa_soup = BeautifulSoup(requests.get(pset_url + thing['href']).content, 'lxml')
                for coisa in coisa_soup.find_all('li'):
                    if 'a file called' in coisa.text:
                        psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
                for coisa in coisa_soup.find_all('p'):
                    if 'a file called' in coisa.text:
                        psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
                    elif 'a program called' in coisa.text:
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
                        psets_urls.append(new_file + "pset/" + "_:_" +
                                          coisa.text.replace("wget ", "").strip("\n"))
                    elif 'file.create' in coisa.text:
                        psets_urls.append(
                            pset_folder + coisa.text.replace('file.create("', '').replace('")', '').strip("\n"))
                    elif 'download.file(' in coisa.text:
                        psets_urls.append(new_file + "pset/" + "_:_" + coisa.text.split('"')[1])

        # gets folders names
        for item in soup.ol.li.next_siblings:
            if str(item) != "\n":
                if "/" in item.a.text:
                    item.a.string.replace_with(item.a.text.replace("/", ""))
                new_file = course + "/" + '0' + \
                    item.a.attrs['href'].replace("/", " ") + item.a.text + '/'
                if not quiet:
                    console.print(
                        f"[bold blue]Scraping week: {'0' + item.a.attrs['href'].replace('/', ' ')} {item.a.text}[/bold blue]")
                files.append(new_file)

                # get other source code urls
                new_url = url + item.a.attrs['href']
                new_soup = BeautifulSoup(requests.get(new_url).content, 'lxml')
                for some in new_soup.find_all('ul'):
                    for someth in some.find_all('li'):
                        for something in someth.find_all('a'):
                            if "Zip" in something.text:
                                src_url = something.attrs['href']
                links.append(new_file + "_:_" + src_url)

                # gets other pset folders
                pset_url = new_url.replace("weeks", "psets")
                pset_soup = BeautifulSoup(requests.get(pset_url).content, 'lxml')
                for thing in pset_soup.find_all('a', href=True):
                    if thing['href'].startswith("http") or thing['href'].startswith("..") or thing['href'].startswith("mail"):
                        pass
                    else:
                        pset_folder = new_file + 'pset/' + thing['href']
                        psets_folders.append(pset_folder)

                        # trying to get other psets urls
                        coisa_soup = BeautifulSoup(requests.get(
                            pset_url + thing['href']).content, 'lxml')
                        for coisa in coisa_soup.find_all('li'):
                            if 'a file called' in coisa.text:
                                psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
                        for coisa in coisa_soup.find_all('p'):
                            if 'a file called' in coisa.text:
                                psets_urls.append(pset_folder + coisa.code.text.strip("\n"))
                            elif 'a program called' in coisa.text:
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
                                psets_urls.append(new_file + "pset/" + "_:_" +
                                                  coisa.text.replace("wget ", "").strip("\n"))
                            elif 'download.file(' in coisa.text:
                                psets_urls.append(new_file + "pset/" + "_:_" +
                                                  coisa.text.split('"')[1])
                            elif 'file.create' in coisa.text:
                                psets_urls.append(
                                    pset_folder + coisa.text.replace('file.create("', '').replace('")', '').strip("\n"))

        psets = []

        for x in files:
            if x != (course + "/"):
                psets.append(x + "pset/")

    lista.extend(files)
    if not nsc:
        lista.extend(links)
    if course != 'CS50 SQL':
        psets[-1] = psets[-1].replace("pset/", "Project/")
    lista.extend(psets)
    lista.extend(psets_folders)
    lista.extend(psets_urls)
    return lista

# Sequence of functions that will finish the job


def fix_py() -> None:
    # fixes CS50 Python week 6 and 8
    shutil.move("./CS50 Python/08 Object-Oriented Programming/pset/shirtificate.png",
                "./CS50 Python/08 Object-Oriented Programming/pset/shirtificate/")
    shutil.move("./CS50 Python/06 File IO/pset/sicilian.csv",
                "./CS50 Python/06 File IO/pset/pizza/")
    shutil.move("./CS50 Python/06 File IO/pset/regular.csv", "./CS50 Python/06 File IO/pset/pizza/")
    os.remove("./CS50 Python/06 File IO/pset/shirt/shirt.png")
    shutil.move("./CS50 Python/06 File IO/pset/shirt.png", "./CS50 Python/06 File IO/pset/shirt/")
    shutil.move("./CS50 Python/06 File IO/pset/before.csv",
                "./CS50 Python/06 File IO/pset/scourgify/")
    shutil.move("./CS50 Python/06 File IO/pset/before1.jpg", "./CS50 Python/06 File IO/pset/shirt/")
    shutil.move("./CS50 Python/06 File IO/pset/before2.jpg", "./CS50 Python/06 File IO/pset/shirt/")
    shutil.move("./CS50 Python/06 File IO/pset/before3.jpg", "./CS50 Python/06 File IO/pset/shirt/")


def fix_x() -> None:
    # fixes CS50x week 4
    shutil.rmtree("./CS50x/Week 4 Memory/pset/filter/")


def fix_sql() -> None:
    os.makedirs("./CS50 SQL/06 Scaling/pset/dont-panic/java/", exist_ok=True)
    os.makedirs("./CS50 SQL/06 Scaling/pset/dont-panic/python/", exist_ok=True)
    shutil.rmtree("./CS50 SQL/05 Optimizing/pset/your.harvard/")
    for file in os.listdir("./CS50 SQL/06 Scaling/pset/dont-panic-java/"):
        shutil.move("./CS50 SQL/06 Scaling/pset/dont-panic-java/" +
                    file, "./CS50 SQL/06 Scaling/pset/dont-panic/java/")
    for file in os.listdir("./CS50 SQL/06 Scaling/pset/dont-panic-python/"):
        shutil.move("./CS50 SQL/06 Scaling/pset/dont-panic-python/" +
                    file, "./CS50 SQL/06 Scaling/pset/dont-panic/python/")
    shutil.rmtree("./CS50 SQL/06 Scaling/pset/dont-panic-java/")
    shutil.rmtree("./CS50 SQL/06 Scaling/pset/dont-panic-python/")


if __name__ == "__main__":
    main()
