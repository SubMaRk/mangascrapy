import os
import re
import time
import json
import random
import emconfig
import datetime
import function
from io import BytesIO
from PIL import Image
import urllib.parse
import requests as rq
from tqdm import tqdm
import latest_user_agents
import concurrent.futures
from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def randomUG():
    all_user_agents = latest_user_agents.get_latest_user_agents()
    user_agents = [user_agent for user_agent in all_user_agents if 'NT' in user_agent and 'Win64' in user_agent]
    return user_agents
    
def getUG():
    user_agents = randomUG()
    return random.choice(user_agents) if user_agents else None

def getHeaders():
    return {
        "User-Agent": getUG(),
        'Accept-Language': 'th-TH,th;q=0.9,en-US;q=0.8,en;q=0.7',
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        'Upgrade-Insecure-Requests': '1',
        "DNT": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Content-Type": "text/html; charset=UTF-8"
    }

def bssoup(url, log, logfile, max_retries=5):
    for _ in range(max_retries):
        try:
            headers = getHeaders()
            response = rq.get(url, headers=headers)
            soup = bs(response.content, 'html.parser')
            text = f"{function.gettime()}: ✅ Successfully fetched page: {url}\n"
            if log:
                function.writeFile(logfile, text)
            return soup
        except Exception as e:
            text = f"{function.gettime()}: ❌ Error: {e}\n"
            if log:
                function.writeFile(logfile, text)
            print(text)
            continue
    return None

def selenium(url, log, logfile, max_retries=5):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features=BlockCredentialedSubresources")
    options.add_argument(f"user-agent={getUG()}")
    options.add_argument("user-data-dir=Z:/Scrapy/Chrome/profile")
    
    prefs = {"profile.default_content_setting_values.cookies": 1}
    options.add_experimental_option("prefs", prefs)
    
    for attempt in range(1, max_retries + 1):
        driver = None
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)

            # Wait until the entire page loads
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # **1. Scroll down to trigger lazy loading**
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Give time for content to load

            soup = bs(driver.page_source, 'html.parser')
            success_message = f"{function.gettime()}: ✅ Successfully fetched page: {url}\n"
            if log:
                function.writeFile(logfile, success_message)
            print(success_message)
            return soup

        except Exception as e:
            if log:
                failure_message = f"{function.gettime()}: ❌ Error: {e}\n"
                function.writeFile(logfile, failure_message)
            print(f"Retry {attempt}/{max_retries} failed: {e}")
            

        finally:
            if driver:
                driver.quit()

    text = f"{function.gettime()}: ❌ Failed to retrieve page after retries.\n"
    if log:
        function.writeFile(logfile, text)
    return None

def find_section(url, soup, log, logpath):
    print(f"{function.gettime()}: Finding section from {url}...")
    try:
        # Section selector dictionary
        section_selectors = {
            1: "div.site-content",
            2: "div.postbody",
            3: "div.series",
            4: "div#content",
            5: "section.content",
            6: "div#sct_content",
            7: "body.custom",
            8: "div#infoarea",
            9: "div.mx-auto.px-4.xl:max-w-7xl.pt-[130px]"
        }

        # Iterate through selectors
        for section_id, selector in section_selectors.items():
            section = soup.select_one(selector)
            if section:
                if log:
                    success_message = f"{function.gettime()}: ✅ Matched Section {section_id}: {selector}\n"
                    function.writeFile(logpath, success_message)
                    print(success_message)
                return section_id, selector, section  # Return section ID, selector, and element

        warning_message = f"{function.gettime()}: ⚠️ Warning: No matching section found.\n"
        if log:
            function.writeFile(logpath, warning_message)
        print(warning_message)
        return None, None, None  # Return None if no match is found

    except Exception as e:
        error_message = f"{function.gettime()}: ❌ Error: {e}\n"
        if log:
            function.writeFile(logpath, error_message)
        print(error_message)
        return None, None, None  # Return None in case of an error

def findData(soup, selectors, multiple=False):
    """Try to find data using multiple selectors (CSS & text search).
    
    - If `multiple=True`, return a list of all matching elements (for genres, etc.).
    - Otherwise, return the first matching element.
    """
    results = []
    for selector in selectors:
        if any(char in selector for char in [' ', '#', '.']):
            # If selector appears to be a CSS selector
            elements = soup.select(selector)
            if elements:
                if multiple:
                    return [element.text.strip() for element in elements if element.text.strip()]
                return elements[0].text.strip() if elements[0].text.strip() else elements[0].get("src", "").strip()
        else:
            # If selector is a plain text label, look inside <h5>
            heading = soup.find("h5", string=lambda text: text and selector in text)
            if heading:
                content_div = heading.find_next("div", class_="summary-content")
                if content_div:
                    if multiple:
                        # Extract text from all <a> tags if they exist
                        genre_links = content_div.find_all("a")
                        if genre_links:
                            return [genre.text.strip() for genre in genre_links if genre.text.strip()]
                        return content_div.text.strip().split(", ")  # Fallback to splitting by commas
                    return content_div.text.strip()
    return results if multiple else "N/A"  # Return empty list if multiple, otherwise "N/A"

def extractChapters(soup, selectors):
    """Extract all chapters from the manga page and sort them properly."""
    for selector in selectors:
        chapter_list = soup.select(selector + ", " + selector + " a")  # Support different structures
        if chapter_list:
            chapters = []
            for chapter in chapter_list:
                chapter_link = chapter.find("a")
                if chapter_link:
                    first_span = chapter_link.find("span", recursive=False)  # Get only the first-level <span>
                    if first_span:
                        # Remove any nested span content
                        for nested in first_span.find_all("span"):
                            nested.extract()
                        chapter_title = first_span.get_text(strip=True)  # Extract clean text without sub-spans
                    else:
                        chapter_title = chapter_link.get_text(strip=True)  # Fallback to full <a> text

                    chapter_url = urllib.parse.unquote(chapter_link["href"])
                    chapters.append({"url": chapter_url, "title": chapter_title})
            return sorted(chapters, key=lambda x: function.sortKey(x['title']))
    return []

def extractData(soup, config):
    """Extract manga data based on provided configuration."""
    manga_data = {}
    for key, selectors in config.items():
        if key == "chapterlist":
            manga_data[key] = extractChapters(soup, selectors)
        elif key == "cover":
            manga_data[key] = findData(soup, selectors)  # Extract image URL
        elif key == "genre":
            manga_data[key] = findData(soup, selectors, multiple=True)  # Extract multiple genres
        else:
            manga_data[key] = findData(soup, selectors)  # General data extraction
    return manga_data

def checkList(soup, log, logpath):
    listselectors = [
        "div.listing-chapters_wrap ul",
        "div#chapterlist ul",
        "ul.main",
        "ul#chapterList",
        "div.eplister ul li",
        ".series-chapterlist li"
    ]
    
    for selector in listselectors:
        if soup.select(selector):
            return True

    # If no chapter list is found, log and return False
    print("Chapter list is missing.")
    if log:
        function.writeFile(logpath, f"{function.gettime()}: Chapter list is missing. Try to get them with Selenium...\n")
    return False

def cutOff(chapterlist, start, end):
    start = int(start) if start else None
    end = int(end) if end else None
    if start is not None and end is not None:
        if start < 1:
            start = 1
        if end > len(chapterlist):
            end = len(chapterlist)
        return chapterlist[start-1:end]
    elif start is not None and end is None:
        if start < 1:
            start = 1
        return chapterlist[start-1:]
    elif start is None and end is not None:
        if end > len(chapterlist):
            end = len(chapterlist)
        return chapterlist[:end]
    else:
        return chapterlist

def checkExist(chapterlist, chapterurls):
    """Returns a list of missing chapters with both title and URL."""
    chapterurllist = {chapter["url"]: chapter["title"] for chapter in chapterlist}
    missing_chapters = [{"title": title, "url": url} for url, title in chapterurllist.items() if url not in chapterurls]
    
    return None if not missing_chapters else missing_chapters

def fetchInfo(url, start, end, output, wThread, iThread, listchapter, nocover, debug, savejson, update, log):
    # Check internet connection
    #function.waitNet()
    cprFile = os.path.join(os.getcwd(), "copyrights.txt")
    htFile = os.path.join(os.getcwd(), "hentai.txt")
    linkFile = os.path.join(os.getcwd(), "link.txt")
    
    if os.path.exists(cprFile):
        cprList = function.readFile(cprFile)
        if url in cprList:
            print(f"{function.gettime()}: ⚠️ The series has been copyrighted in Thailand. Skipping...")
            return
    
    if os.path.exists(htFile):
        hentaiList = function.readFile(htFile)
        if url in hentaiList:
            print(f"{function.gettime()}: ⚠️ The series is Hentai. Skipping...")
            return
        
    url = function.safeDecode(url)
    
    domain = urllib.parse.urlparse(url).netloc
    domain = domain.replace('www.', '')
    domain = domain.split('.')[0]
    
    # Check Target host status
    '''if not function.isOnline(domain):
        print(f"{function.gettime()}: ❌ Host {domain} is offline.")
        exit(1)
    else:
        print(f"{function.gettime()}: 🌐 Host {domain} is online.")'''
    
    # Get now date
    getDate = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Set folder path
    fDown = os.path.join(output, "Download")
    fLog = os.path.join(output, "Logs", f"{getDate}")
    fJson = os.path.join(output, "Data", f"{domain}")
    
    # Create folder if not exists
    function.mkDir(fDown)
    function.mkDir(fLog)
    function.mkDir(fJson)
    
    # Set all log files types
    logFile = os.path.join(fLog, f"full.log")
    noChapter = os.path.join(fLog, f"nochapter.log")
    notDown = os.path.join(fLog, f"notdownloaded.log")
    
    # Check available free space before starting
    if function.checkSpace():
        print(f"{function.gettime()}: ✅ Sufficient space available. Starting process...")
    else:
        print(f"{function.gettime()}: ❌ Not enough free space! Process aborted.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: ❌ Not enough free space! Process aborted.\n")
        exit(1)
    
    # Fetch manga info from url
    soup = bssoup(url, log, logFile)
    
    # Check if the chapter list is missing
    delayList = checkList(soup, log, logFile)
    if delayList is False:
        soup = selenium(url, log, logFile)
    
    # Find section info to know patterns
    section_id, selector, section = find_section(url, soup, log, logFile)
    
    # Check if section is found
    if not section:
        print(f"{function.gettime()}: Section {url} not found. Exiting...")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: Section for {url} not found.\n")
        exit(1)
    
    # Handle found section from ID
    config = emconfig.config(section_id)
    print(f"{function.gettime()}: Fetching information from url: {url}...")
    if log:
        function.writeFile(logFile, f"{function.gettime()}: Fetching information from url: {url}...\n")
    mangaData = extractData(section, config)
    
    if len(mangaData["chapterlist"]) == 0:
        print(f"{function.gettime()}: No chapters found. Exiting...")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: No chapters found.\n")
            function.writeFile(noChapter, f"{url}\n")
        exit(1)
    
    # Cut only chapters that user want
    chapterList = cutOff(mangaData["chapterlist"], start, end)
    
    # Store data to specific variables
    mgTitle = function.sanitizedName(mangaData["title"])
    mgType = mangaData["type"]
    mgGenres = ", ".join(mangaData["genre"])
    mgStatus = mangaData["status"]
    mgCover = mangaData["cover"]
    
    """Pretty print the extracted manga data in a readable format."""
    print("\n================ SERIES INFO ===================")
    print("Title: ", mgTitle)
    print("Type: ", mgType)
    print("Genre(s): ", mgGenres)
    print("Status: ", mgStatus)
    print("Cover: ", mgCover)
    print("Total Chapters: ", len(mangaData["chapterlist"]))
    print("Total Download Count: ", len(chapterList))
    
    if listchapter is True:
        start = start if start is not None else 1
        end = end if end is not None else len(mangaData["chapterlist"])
        print("Chapters:")
        for i in range(len(chapterList)):
            chapterList[i]["title"] = chapterList[i]["title"]
            print(f"{i+1} - {chapterList[i]['title']} | URL: {chapterList[i]['url']}")
        print(f"Chapters: {start} - {end} / Total: {len(mangaData['chapterlist'])}")
        exit(0)
    else:
        start = start if start is not None else 1
        end = end if end is not None else len(mangaData["chapterlist"])
        for i in range(len(chapterList)):
            chapterList[i]["title"] = chapterList[i]["title"]
            print(f"{i+1} - {chapterList[i]['title']} | URL: {chapterList[i]['url']}")
        print(f"Chapters: {start} - {end} / Total: {len(mangaData['chapterlist'])}")
        
    # Save JSON data
    if savejson is True:
        jsonFile = os.path.join(fJson, f"{mgTitle}.json")
        print(f"{function.gettime()}: 💾 Saving data to: {jsonFile}...")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: 💾 Saving data to: {jsonFile}...\n")
        if not os.path.exists(jsonFile):
            function.savejson(jsonFile, mgTitle=mgTitle, mgtype=mgType, mggenres=mgGenres, mgstatus=mgStatus, chaptercount=len(mangaData["chapterlist"]))

            mgTitle, mgType, mgGenres, mgStatus, chaptercount, chapterurls = function.readjson(jsonFile)
            print(f"{function.gettime()}: 📁 JSON data saved to {jsonFile}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: 📁 JSON data saved to {jsonFile}...\n")
        else:
            # Update new information to file
            function.savejson(jsonFile, mgTitle=mgTitle, mgtype=mgType, mggenres=mgGenres, mgstatus=mgStatus, chaptercount=len(mangaData["chapterlist"]))

            print(f"{function.gettime()}: 🔄 JSON data updated to {jsonFile}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: 🔄 JSON data updated to {jsonFile}...\n")
            mgTitle, mgType, mgGenres, mgStatus, chaptercount, chapterurls = function.readjson(jsonFile)
    
    if update is True:
        jsonFile = os.path.join(fJson, f"{mgTitle}.json")
        function.savejson(jsonFile, mgtitle=mgTitle, mgtype=mgType, mggenres=mgGenres, mgstatus=mgStatus, chaptercount=len(mangaData["chapterlist"]))
        print(f"{function.gettime()}: 🔄 JSON data updated to {jsonFile}")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: 🔄 JSON data updated to {jsonFile}...\n")
    
    # Check if chapters exist
    if savejson is True:
        notLoad = checkExist(chapterList, chapterurls)
        if notLoad is None:
            print(f"{function.gettime()}: All chapters of {url} are exist.")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: All chapters of {url} are exist.\n")
    
            exit(0)
        else:
            print(f"{function.gettime()}: Missing chapters: \n{'\n'.join(chap['url'] for chap in notLoad)}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: Missing chapters of {url}: \n{'\n'.join(chap['url'] for chap in notLoad)}\n")
            print("Downloading missing chapters...")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: Downloading missing chapters from {url}...\n")
            chapterList = notLoad
    
    # Create manga folder
    mgFolder = os.path.join(fDown, f"{mgTitle}")
    function.mkDir(mgFolder)
    
    # Start processing chapters with multi-threading
    workers = wThread
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_chapter = {}  # Dictionary to track futures

        for i, chapter in enumerate(chapterList):
            chapterUrl = str(chapter["url"])
            chapterTitle = str(chapter["title"])

            if not chapterUrl or not chapterTitle:
                print(f"{function.gettime()}: ⚠️ Skipping chapter {chapterUrl}: Missing title or URL.")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: ⚠️ Skipping chapter {chapterUrl}: Missing title or URL.\n")
                continue

            # Get chapter number and create folder for it
            chapterNumber = function.getchapter(str(chapterTitle))
            if not chapterNumber:
                mgID = function.mangaID(url)
                chID = function.mangaID(chapter)
                chapterNumber = function.numChapter(mgID, chID)

            print(f"{function.gettime()}: 🏁 Submitting chapter {i + 1}/{len(chapterList)} -> {chapterUrl}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: 🏁 Submitting chapter {i + 1}/{len(chapterList)} -> {chapterUrl}\n")

            # Submit the task and store the future
            if savejson is True:
                future = executor.submit(processChapter, chapterUrl, chapterTitle, chapterNumber, mgFolder, iThread, debug, savejson, log, logFile, notDown, jsonFile)
                future_to_chapter[future] = chapterUrl
            else:
                future = executor.submit(processChapter, chapterUrl, chapterTitle, chapterNumber, mgFolder, iThread, debug, savejson, log, logFile, notDown)
                future_to_chapter[future] = chapterUrl

        # Monitor completion
        for future in concurrent.futures.as_completed(future_to_chapter):
            chapterUrl = future_to_chapter[future]
            try:
                future.result()  # This raises any exceptions that occurred in the thread
                print(f"{function.gettime()}: ✅ Successfully processed {chapterUrl}")
            except Exception as e:
                print(f"{function.gettime()}: ❌ Error processing {chapterUrl}: {e}")
    
    if os.path.exists(linkFile):
        linkList = function.readFile(linkFile)
        if url not in linkList:
            function.writeFile(linkFile, f"{url}\n")

def processChapter(chapterUrl, chapterTitle, chapterNumber, mgFolder, iThread, debug, savejson, log, logFile, notDown, jsonFile=None):
    soup = bssoup(chapterUrl, log, logFile)
    chapterFolder = f"Chapter-{chapterNumber}"
    chapterPath = os.path.join(mgFolder, chapterFolder)
    function.mkDir(chapterPath)
    
    # Check images elements have been existing
    if detectEncrypt(soup) is True:
        print(f"{function.gettime()}: Found encrypted images from {chapterUrl}.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: Found encrypted images from {chapterUrl}.\n")
        captureImg(chapterUrl, chapterNumber, chapterPath, debug, savejson, log, logFile, notDown)
    else:
        print(f"{function.gettime()}: No encrypted images detected.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: No encrypted images detected in {chapterUrl}.\n")
        # Find images
        imgList = findImg(soup)
        print(f"{function.gettime()}: Found {len(imgList)} images from {chapterUrl}.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: Found {len(imgList)} images from {chapterUrl}.\n")
        
        print(f"{function.gettime()}: inititializing to downlad image list from {chapterUrl}.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: inititializing to downlad image list from {chapterUrl}.\n")
        workers = iThread
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_image = {}  # Dictionary to track futures
            for i, imgUrl in enumerate(imgList):
                print(f"{function.gettime()}: 🏁 Submitting image {i + 1}/{len(imgList)} -> {imgUrl}")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: 🏁 Submitting chapter {i + 1}/{len(imgList)} -> {imgUrl}\n")
                    
                future = executor.submit(dlImg, i, imgUrl, chapterNumber, chapterUrl, chapterPath, debug, log, logFile, notDown)
                future_to_image[future] = imgUrl
                
            # Monitor completion
            for future in concurrent.futures.as_completed(future_to_image):
                imgUrl = future_to_image[future]
                try:
                    future.result()  # This raises any exceptions that occurred in the thread
                except Exception as e:
                    print(f"{function.gettime()}: ❌ Error downloading image: {imgUrl}: {e}")
                    if log:
                        function.writeFile(logFile, f"{function.gettime()}: ❌ Error downloading image: {imgUrl}\n")
        
        # Check downloaded image files
        countDown = function.countFiles(chapterPath)
        if len(imgList) != countDown:
            print(f"{function.gettime()}: ⚠️ Image count mismatch: {countDown} / {len(imgList)}.")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: ⚠️ Image count mismatch: {countDown} / {len(imgList)}.\n")
            function.writeFile(notDown, f"{chapterUrl}\n")
        else:
            print(f"{function.gettime()}: ✅ Image count match: {countDown} / {len(imgList)}.")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: ✅ Image count match: {countDown} / {len(imgList)}.\n")
            
            # Save JSON data
            if savejson is True:
                function.savejson(jsonFile, chaptertitle=chapterTitle, chapterurl=chapterUrl)
                print(f"{function.gettime()}: 💾 JSON data updated to {jsonFile}.")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: 💾 JSON data updated to {jsonFile}.\n")

    return None

def detectEncrypt(soup):
    # Check for Tiled Images (background-image with offsets)
    if soup.find(style=re.compile(r"background-image:\s*url\((.*?)\)")):
        print(f"{function.gettime()}: ⚠️ Tiled background images detected!")
        return True
    
    # Check for Encrypted Canvas Images
    for canvas in soup.find_all("canvas"):
        if canvas.get("data-url"):  # Direct reference in the attribute
            print(f"{function.gettime()}: ⚠️ Encrypted canvas image detected.")
            return True
        print(f"{function.gettime()}: ⚠️ Encrypted canvas image detected (JS-processed).")
        return True

    # Check for JavaScript-Obfuscated Images (eval function obfuscation)
    if re.search(r"eval\(function\(p,a,c,k,e,d\)", soup.text):
        print(f"{function.gettime()}: ⚠️ JavaScript-obfuscated image detected!")
        return True

    # Check for DisplayImage divs with no direct <img> tag (likely JS-rendered images)
    for div in soup.find_all("div", class_="displayImage"):
        if not div.find("img") and "style" in div.attrs:
            print(f"{function.gettime()}: ⚠️ Hidden images detected in 'displayImage' div.")
            return True

    print(f"{function.gettime()}: ✅ No encrypted images detected.")
    return False

def checkJson(soup):
    print(f"{function.gettime()}: 🔎 Trying to find images from json script...")
    # Check if json script exists
    jsonScript = soup.find("script", string=re.compile(r'ts_reader\.run'))
    if not jsonScript:
        print(f"{function.gettime()}: ❌ No json script found.")
        return []
    else:
        pattern = r'ts_reader\.run\((.+?)\)'
        match = re.search(pattern, jsonScript.string)
        if match:
            # Fix if string has compressed
            jsonText = match.group(1)
            jsonText = re.sub(r'!1', 'true', jsonText)
            jsonText = re.sub(r'!0', 'false', jsonText)
            jsonData = json.loads(jsonText)
            
            # Check if images exist
            if 'sources' in jsonData and len(jsonData['sources']) > 0:
                return jsonData['sources'][0].get('images', [])
    return []

def checkReaddiv(soup):
    print(f"{function.gettime()}: 🔎 Trying to find images from read div...")

    # Possible reader div selectors
    readDivs = [
        "div#readerarea",
        "div.reader-area",
        "div.reader-area-main",
        "div.reading-content",
    ]

    for selector in readDivs:
        div_element = soup.select_one(selector)  # Select the first matching div
        if div_element:
            img_tags = div_element.find_all("img")  # Find all <img> inside the div
            if img_tags:
                images = []
                for img in img_tags:
                    src = img.get("data-src") or img.get("src")
                    
                    # If srcset exists, take the first URL (highest quality version)
                    if not src and img.get("srcset"):
                        src = img["srcset"].split(",")[0].split()[0]

                    if src:  # Ensure src is not None
                        images.append(src)

                return images if images else []

    return []

def findImg(soup):
    imgList = checkJson(soup)
    if not imgList:
        imgList = checkReaddiv(soup)
        return imgList
    return imgList if imgList else []

def dlImg(i, imgUrl, chapterNumber, chapterUrl, chapterPath, debug, log, logFile, notDown):
    print(f"{function.gettime()}: ⏳ Downloading image {imgUrl}...")
    excludeFile = "excludedomain.txt"

    # Check internet connection
    #function.waitNet()

    notDownList = function.readFile(notDown) if os.path.exists(notDown) else []
    excludeDomains = function.readFile(excludeFile) if os.path.exists(excludeFile) else []
    
    domain = urllib.parse.urlparse(imgUrl).netloc
    domain = domain.replace('www.', '')
    
    if domain in excludeDomains:
        print(f"{function.gettime()}: ⚠️ Excluding domain: {domain}")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: ⚠️ Excluding domain: {domain}\n")
        if chapterUrl not in notDownList:
            function.writeFile(notDown, f"{chapterUrl}\n")
        return None

    # Fix URLs missing scheme
    if imgUrl.startswith('//'):
        imgUrl = 'https:' + imgUrl
        if log:
            function.writeFile(logFile, f"{function.gettime()}: ⚠️ Added 'https:' to image link.\n")

    # Fix domain name change
    imgUrl = imgUrl.replace("manga168.com", "manga168.net")

    # Check the file extension
    fileExtension = os.path.splitext(imgUrl)[1]
    if fileExtension == '.webppng':
        imgUrl = imgUrl.replace(".webppng", ".webp")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: ⚠️ Changed the url to {imgUrl}.\n")

    if not fileExtension:
        print(f"{function.gettime()}: ⚠️ No file extension found for {imgUrl}.")
        if log:
            function.writeFile(logFile, f"{function.gettime()}: ⚠️ No file extension for {imgUrl}.\n")
        if chapterUrl not in notDownList:
            function.writeFile(notDown, f"{chapterUrl}\n")
        return None

    # Set image file name
    imgName = f"Chapter-{chapterNumber}_image_{i}{fileExtension}"
    imgPath = os.path.join(chapterPath, imgName)

    # Check if file exists and verify its size
    if os.path.isfile(imgPath):
        # Validate the downloaded image
        isValid = function.checkImg(imgPath)
        if isValid == True:
            print(f"{function.gettime()}: ✅ Downloaded and verified: {imgUrl}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: ✅ Downloaded and verified:  {imgUrl}.\n")
            return
        else:
            print(f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying...")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying:  {imgUrl}.\n")
            os.remove(imgPath)
    # Download image with retry, timeout, and progress bar
    retries = 6
    for attempt in range(retries):
        #function.waitNet()  # Re-check internet before retry
        try:
            response = rq.get(imgUrl, headers=getHeaders(), stream=True, timeout=300)
            response.raise_for_status()
            
            total_length = int(response.headers.get('Content-Length', 0))
            formatted_size = function.formatSize(total_length) if total_length else "Unknown size"
            
            with open(imgPath, 'wb') as f:
                if total_length > 0:
                    with tqdm(total=total_length, unit='B', unit_scale=True, desc=f"Downloading {imgName} ({formatted_size})") as bar:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)

            # Validate the downloaded image
            localSize = os.path.getsize(imgPath)
            isValid = function.checkImg(imgPath)
            checkSize = function.compareSize(int(total_length), int(localSize))
            if int(total_length) > 0:
                if isValid == True and checkSize == True:
                    print(f"{function.gettime()}: ✅ Downloaded and verified: {imgUrl} => {imgName}")
                    if log:
                        function.writeFile(logFile, f"{function.gettime()}: ✅ Downloaded and verified: {imgUrl} => {imgName}.\n")
                    return
                else:
                    print(f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying...")
                    if log:
                        function.writeFile(logFile, f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying:  {imgUrl}.\n")
                    if os.path.exists(imgPath):
                        os.remove(imgPath)
            else:
                if isValid == True:
                    print(f"{function.gettime()}: ✅ Downloaded and verified: {imgUrl} => {imgName}")
                    if log:
                        function.writeFile(logFile, f"{function.gettime()}: ✅ Downloaded and verified: {imgUrl} => {imgName}.\n")
                    return
                else:
                    print(f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying...")
                    if log:
                        function.writeFile(logFile, f"{function.gettime()}: ⚠️ Image is corrupt or incomplete, retrying:  {imgUrl}.\n")
                    if os.path.exists(imgPath):
                        os.remove(imgPath)

        except rq.exceptions.HTTPError as e:
            if response.status_code == 403:
                print(f"{function.gettime()}: 🔴 403 Forbidden! Retrying with new headers...")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: 🔴 403 Forbidden! Retrying with new headers:  {imgUrl}.\n")
                if os.path.exists(imgPath):
                    os.remove(imgPath)
                return None
            elif response.status_code == 404:
                print(f"{function.gettime()}: 🔴 404 Not Found!")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: 🔴 404 Not Found! Retrying:  {imgUrl}.\n")
                if os.path.exists(imgPath):
                    os.remove(imgPath)
                return None
            else:
                print(f"{function.gettime()}: ❌ HTTP error: {e}")
                if log:
                    function.writeFile(logFile, f"{function.gettime()}: ❌ HTTP error: {e}.\n")
                if os.path.exists(imgPath):
                    os.remove(imgPath)

        except rq.exceptions.RequestException as e:
            print(f"{function.gettime()}: ❌ Attempt {attempt+1} failed: {e}")
            if log:
                function.writeFile(logFile, f"{function.gettime()}: ❌ Attempt {attempt+1} failed: {e}.\n")

        # Exponential backoff before retrying
        time.sleep(1 ** attempt)

    print(f"{function.gettime()}: ❌ All retry attempts failed for {imgUrl}")
    if log:
        function.writeFile(logFile, f"{function.gettime()}: ❌ All retry attempts failed for {imgUrl}.\n")
    if chapterUrl not in notDownList:
        function.writeFile(notDown, f"{chapterUrl}\n")
    return None

def captureImg(chapterUrl, chapterNumber, chapterPath, debug, savejson, log, logFile, notDown):
    # Initialize selenium
    options = Options()
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-infobars")
    options.add_argument("--window-size=900,1200")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-blink-features=BlockCredentialedSubresources")
    options.add_argument(f"user-agent={getUG()}")
    
    prefs = {"profile.default_content_setting_values.cookies": 1}
    options.add_experimental_option("prefs", prefs)
    
    attempt = 0
    maxRetires = 3
    
    for attempt in range(maxRetires):
        try:
            #function.waitNet()
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            driver.get(chapterUrl)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            readDiv = getReadDiv(driver)
            if readDiv:
                rmElements(driver, readDiv)
                print("Remove unnecessary elements.")
                time.sleep(1)
                windowSize(driver)
                print("Resize window size")
                time.sleep(0.5)
                ranMouse(driver)
                print("Random mouse")
                time.sleep(1)
                scrollCheckHeight(driver)
                print("Check scroll height")
                time.sleep(0.5)
                
                # Scroll to top of page
                driver.execute_script("window.scrollTo(0, 0)")
                time.sleep(0.5)
                
                # **Wait for all images to load before capturing**
                chapturing(driver, readDiv, chapterNumber, chapterPath, log, logFile)
                
            break
        except Exception as e:
            print(f"{function.gettime()}: ❌ WebDriver error: {e}")
            attempt += 1
            time.sleep(3)
            driver.quit()
    driver.quit()

def getReadDiv(driver):
    print(f"{function.gettime()}: Finding read element from page.")
    
    # Possible reader div selectors
    readDivs = [
        "div#readerarea",
        "div.reader-area",
        "div.reader-area-main",
        "div.reading-content",
    ]
    
    for div in readDivs:
        try:
            driver.find_element(By.CSS_SELECTOR, div)  # Just check if it exists
            print(f"{function.gettime()}: ✅ Read element found: {div}")
            return div  # Return the selector string, not the element
        except Exception:
            continue
    
    print(f"{function.gettime()}: ❌ No read element found.")
    return None  # Return None if no element is found

def ranMouse(driver):
    print("Randomly moving mouse...")
    # Get the browser window size
    window_size = driver.get_window_size()
    max_x = window_size['width'] - 100
    max_y = window_size['height'] - 100

    # Generate random coordinates
    x = random.randint(0, max_x)
    y = random.randint(0, max_y)

    # Create an ActionChains object
    actions = ActionChains(driver)

    # Move the mouse to the random coordinates
    actions.move_by_offset(x, y).perform()
    time.sleep(0.5)
    
def windowSize(driver):
    print("Resizing window size...")
    # Get the current window size
    current_size = driver.get_window_size()

    # Decrease the width and height by 1 pixel
    width = current_size['width'] - 1
    height = current_size['height']

    # Set the new window size
    driver.set_window_size(width, height)
    time.sleep(0.5)

    # Get the current window size
    current_size = driver.get_window_size()

    # Decrease the width and height by 1 pixel
    width = current_size['width'] - 1
    height = current_size['height']

    # Set the new window size
    driver.set_window_size(width, height)

def rmElements(driver, readDiv):
    print("Removing elements...")
    try:
        # Wait until the document.readyState is 'complete'
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//body/*')))
    except Exception as e:
        print(f"Page load timed out: {e}")

    try:
        # Wait for the div to be present
        target = driver.find_element(By.CSS_SELECTOR, readDiv)
    except Exception as e:
        print(f"Error: {e}")
        return None
    
    # Traverse up the DOM tree to find all parent elements
    parent_elements = []
    parent_element = target
    while parent_element.tag_name != 'html':
        parent_element = parent_element.find_element(By.XPATH, '..')
        parent_elements.append(parent_element)
    
    # Hide all elements except the target div (using JavaScript)
    driver.execute_script("""
        var elements = document.querySelectorAll('*');
        for (var i = 0; i < elements.length; i++) {
            elements[i].style.display = 'none';
        }
    """)
        
    # Show the target div and its parent elements
    driver.execute_script("""
        var targetDiv = arguments[0];
        targetDiv.style.display = 'block';
        var childNodes = targetDiv.getElementsByTagName('*');
        for (var i = 0; i < childNodes.length; i++) {
            if (childNodes[i].tagName.toLowerCase() !== 'script') {
                childNodes[i].style.display = 'block';
            }
        }
        var parentElements = arguments[1];
        for (var i = 0; i < parentElements.length; i++) {
            parentElements[i].style.display = 'block';
        }
    """, target, parent_elements)

    # Execute JavaScript to hide the scrollbar
    driver.execute_script(
        """
        var style = document.createElement('style');
        style.innerHTML = '::-webkit-scrollbar { display: none; }';
        document.head.appendChild(style);
        """
    )

    # Set width to auto for specified images
    driver.execute_script("""
        var windowWidth = window.innerWidth + 'px';
        var container = document.querySelectorAll('.container, #content, .wrapper, .postarea, .reading-content, .read-container, .entry-content_wrap, .main-col-inner');
        container.forEach(function(div) {
            div.style.width = windowWidth;
            div.style.margin = 'unset';
            div.style.padding = 'unset';
            div.style.lineHeight = 'unset';
        });
    """)

    driver.execute_script("""
        var images = document.querySelectorAll('img');
        images.forEach(function(img) {
            img.style.width = '100%';
            img.style.margin = 'unset';
            img.style.padding = 'unset';
        });
    """)

    driver.execute_script("""
        var container = document.querySelectorAll('.scrollToTop, #text-chapter-toolbar');
        container.forEach(function(div) {
            div.style.opacity = '0';
            div.style.display = 'none';
        });
    """)

def scrollCheckHeight(driver):
    print("Checking height of element...")
    height = driver.execute_script("return document.body.scrollHeight;")
    
    # Scroll down until the height no longer changes
    while True:
        driver.execute_script(f"window.scrollBy(0, {height});")
        #ranMouse(driver)
        time.sleep(2)
        
        # Calculate the new total height
        newHeight = driver.execute_script("return document.body.scrollHeight;")
        
        if newHeight == height:
            break
        
        height = newHeight

def chapturing(driver, readDiv, chapterNumber, chapterPath, log, logFile):
    # Make folder to save the images
    if not os.path.exists(chapterPath):
        os.makedirs(chapterPath)

    # Get page dimensions
    total_height = driver.execute_script("return document.documentElement.scrollHeight")
    viewport_width = driver.execute_script("return document.documentElement.scrollWidth")
    viewport_height = driver.execute_script("return window.innerHeight")

    # Scroll & capture screenshots separately
    scroll_y = 0
    screenshot_count = 1

    while scroll_y + viewport_height < total_height:  # Capture full viewport sections first
        driver.execute_script(f"window.scrollTo(0, {scroll_y})")
        time.sleep(0.5)  # Allow content to load properly

        # Capture screenshot
        screenshot = driver.get_screenshot_as_png()
        img = Image.open(BytesIO(screenshot))

        # Save each section separately
        image_path = os.path.join(chapterPath, f"Chapter-{chapterNumber}_image_{screenshot_count}.png")
        img.save(image_path)
        print(f"Saved: {image_path}")

        # Move to the next section
        scroll_y += viewport_height
        screenshot_count += 1

    # **Fix: Resize window for the last section**
    remaining_height = total_height - scroll_y  # Only capture what's left
    if remaining_height > 0:
        driver.set_window_size(viewport_width, remaining_height)  # Resize window to fit last part
        driver.execute_script(f"window.scrollTo(0, {scroll_y})")
        time.sleep(1)

        screenshot = driver.get_screenshot_as_png()
        img = Image.open(BytesIO(screenshot))
        image_path = os.path.join(chapterPath, f"Chapter-{chapterNumber}_image_{screenshot_count}.png")
        img.save(image_path)
        print(f"✅ Final capture saved (resized window): {image_path}")

    print(f"✅ Chapter {chapterNumber} screenshots saved in {chapterPath}")

    # Restore window size after capturing
    driver.set_window_size(viewport_width, viewport_height)

def waitForImages(driver, readDiv, timeout=60):
    """
    Waits until all images inside `readDiv` are fully loaded.
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: all(img.get_attribute("complete") == "true" for img in d.find_elements(By.CSS_SELECTOR, f"{readDiv} img"))
        )
        print("✅ All images loaded successfully!")
        return True
    except Exception:
        print("⚠️ Timeout: Some images may not have loaded completely.")
        return False