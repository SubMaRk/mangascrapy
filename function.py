import os
import re
import sys
import json
import time
import socket
from PIL import Image
import requests
import urllib.parse
import latest_user_agents

def cls():
    """Clear the terminal screen across all operating systems."""
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
    except Exception:
        sys.stdout.write("\033c")  # ANSI escape code for clearing the screen
        sys.stdout.flush()


def mkDir(path):
    if not os.path.exists(path):
        print(f"{gettime()}: ❌ Folder {path} not created.")
        print(f"{gettime()}: 📁 Try to create folder {path}...")
        os.makedirs(path)
        print(f"{gettime()}: 📁 Folder {path} created.")
    else:
        print(f"{gettime()}: ✅ Folder {path} already exists.")
        pass
    
def delDir(path):
    if os.path.exists(path):
        os.rmdir(path)
        print(f"Removed folder {path}.")
    else:
        print(f"Folder {path} does not exist.")
        pass

def writeFile(path, content):
    with open(path, "a+", encoding='utf-8') as file:
        file.write(content)
        
def readFile(path):
    with open(path, "r", encoding='utf8') as file:
        return file.readlines()

def countFiles(path):
    files = os.listdir(path)
    count = len(files)
    
    return count

def savejson(path, mgTitle=None, mgtype=None, mggenres=None, mgstatus=None, chaptercount=None, chaptertitle=None, chapterurl=None):
    title_prefix = "Title"
    type_prefix = "Type"
    genre_prefix = "Genres"
    status_prefix = "Status"
    count_prefix = "Count"
    savechapters = "ChapterURLs"

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    else:
        data = {
            title_prefix: mgTitle,
            type_prefix: mgtype,
            genre_prefix: mggenres,
            status_prefix: mgstatus,
            count_prefix: chaptercount,
            savechapters: {}
        }

    if mgTitle is not None:
        data[title_prefix] = mgTitle
    if mgtype is not None:
        data[type_prefix] = mgtype
    if mggenres is not None:
        data[genre_prefix] = mggenres
    if mgstatus is not None:
        data[status_prefix] = mgstatus
    if chaptercount is not None:
        data[count_prefix] = chaptercount

    if chaptertitle and chapterurl:
        if chapterurl not in data[savechapters]:
            data[savechapters][chapterurl] = chaptertitle
        else:
            print(f"Chapter URL '{chapterurl}' already exists. Skipping addition.")

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def readjson(path):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    mgtitle = data["Title"]
    mgtype = data["Type"]
    mggenres = data["Genres"]
    mgStatus = data["Status"]
    chaptercount = data["Count"]
    chapterurls = data["ChapterURLs"]

    return mgtitle, mgtype, mggenres, mgStatus, chaptercount, chapterurls

def get_user_agent():
    all_user_agents = latest_user_agents.get_latest_user_agents()

    chrome_user_agent = next(user_agent for user_agent in all_user_agents if 'Chrome/' and 'NT' and 'Win64' in user_agent)

    return chrome_user_agent


def getHeaders():
    user_agent = get_user_agent()
    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    return headers

def isOnline(host, port=443, timeout=10):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(f"Host {host} is offline: {ex}")
        return False
    
def checkNet():
    try:
        response = requests.get("https://www.google.com", timeout=15)
        return response.status_code == 200
    except (requests.ConnectionError,requests.Timeout):
        return False
    
def waitNet():
    print(f'{gettime()}: ⏳ Watiting for internet connection...')
    while not checkNet():
        print(f'{gettime()}: ⚠️ No internet connection. Retrying in 15 seconds...')
        time.sleep(15)
    print(f"{gettime()}: 🌐 Internet connection detected. Continuing...")
    
def getchapter(title):
    numbers = re.findall(r'\d+', title)

    if len(numbers) == 6:
        return '-'.join(numbers)
    elif len(numbers) == 5:
        return '-'.join(numbers)
    elif len(numbers) == 4:
        return '-'.join(numbers)
    elif len(numbers) == 3:
        return '-'.join(numbers)
    elif len(numbers) == 2:
        return '-'.join(numbers)
    elif len(numbers) == 1:
        return numbers[0]
    else:
        return ''
    
def findchapternum(title):
    if 'ตอน' in title:
        result = re.split(r'(?=ตอน)', title)[-1]
    elif 'Chapter' in title:
        result = re.split(r'(?=Chapter)', title)[-1]
    else:
        result = re.split(r'\d+', title)[-1]

    numbers = re.findall(r'\d+', result)

    if len(numbers) == 6:
        return '-'.join(numbers)
    elif len(numbers) == 5:
        return '-'.join(numbers)
    elif len(numbers) == 4:
        return '-'.join(numbers)
    elif len(numbers) == 3:
        return '-'.join(numbers)
    elif len(numbers) == 2:
        return '-'.join(numbers)
    elif len(numbers) == 1:
        return numbers[0]
    else:
        return ''
    
def mangaid(manga_url):
    pattern = re.compile(r"([^/]+)/?$")
    decode_url = urllib.parse.urlparse(manga_url)
    urlpath = decode_url.path
    match = pattern.search(urlpath)
    if match:
        return match.group(1)
    else:
        return ''
    
def gettime():
    return time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())

def sortKey(name):
    """Custom sorting key to handle both numbers and text in chapter names."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', name)]

def sanitizedName(name):
    """Sanitizes a string by removing invalid characters for file names."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', name).strip()

def getFilesize(filepath):
    """Returns file size in bytes if the file exists, otherwise returns None."""
    return os.path.getsize(filepath) if os.path.isfile(filepath) else None

def formatSize(size):
    """Format file size to human-readable format."""
    suffixes = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size >= 1024 and i < len(suffixes) - 1:
        size /= 1024
        i += 1
    return f"{size:.2f} {suffixes[i]}"

def checkImg(imgPath):
    """Verify if an image is valid using PIL."""
    try:
        with Image.open(imgPath) as img:
            img.verify()
        return True
    except Exception:
        return False
    
def mangaID(url):
    pattern = re.compile(r"([^/]+)/?$")
    decode_url = urllib.parse.urlparse(url)
    urlpath = decode_url.path
    match = pattern.search(urlpath)
    if match:
        return match.group(1)
    else:
        return ''
    
def numChapter(mgID, chapterID):
    # Use re.sub to remove the title from the chapter_title
    text = re.sub(f"^{mgID}", "", chapterID).strip()

    # Use regular expression to find all groups of digits in the input string
    numbers = re.findall(r'\d+', text)

    # If there are two numbers, format them as "u-v-w-x-y-z"
    if len(numbers) == 6:
        return '-'.join(numbers)
    elif len(numbers) == 5:
        return '-'.join(numbers)
    elif len(numbers) == 4:
        return '-'.join(numbers)
    elif len(numbers) == 3:
        return '-'.join(numbers)
    elif len(numbers) == 2:
        return '-'.join(numbers)
    elif len(numbers) == 1:
        return numbers[0]
    else:
        return ''