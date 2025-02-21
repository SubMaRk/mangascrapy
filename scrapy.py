import argparse
import os
import series

def arr():
    parser = argparse.ArgumentParser(
        description="📖 Manga Scraper CLI - Download manga series, chapters, or search for manga.",
        epilog="🔹 Examples:\n"
               "  --:: For downloading series ::--\n"
               "  python scrapy.py --murl 'https://manga.com/series' --start 1 --end 10 --workthreads 4 --imagethreads 4 --output '/path'\n"
               "  python scrapy.py -m 'https://manga.com/series' -s 1 -e 10 -wt 4 -it 4 -o '/path'\n"
               "  --:: For downloading a chapter ::--\n"
               "  python script.py --curl 'https://manga.com/chapter' --imagethreads 4 --output '/path'\n"
               "  python script.py -c 'https://manga.com/chapter' -it 4 -o '/path'\n"
               "  --:: For searching manga ::--\n"
               "  python script.py --search 'One Piece' --host 'manga-site.com'\n"
               "  python script.py -f 'One Piece' -hs 'manga-site.com'\n",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # 🌟 Common Options
    common_group = parser.add_argument_group("🔧 Common Options")
    common_group.add_argument('--output', '-o', type=str, help="📁 Output path (default: current directory).")
    common_group.add_argument('--imagethreads', '-it', type=int, help="📸 Threads for image downloads (default: 1).")
    common_group.add_argument('--workthreads', '-wt', type=int, help="⚙️ Threads for processing (default: 1).")

    # 📚 Series Scraping
    series_group = parser.add_argument_group("📚 Series Scraping")
    series_group.add_argument('--murl', '-m', type=str, help="🔗 Manga URL to scrape.")
    series_group.add_argument('--listchapter', '-lc', action='store_true', help="📜 List chapters without downloading.")
    series_group.add_argument('--start', '-s', type=int,  help="⏳ Start chapter")
    series_group.add_argument('--end', '-e', type=int, help="⏹️ End chapter.")
    series_group.add_argument('--nocover', '-nc', action='store_true', help="❌ Not download cover image.")

    # 📄 Chapter Scraping
    chapter_group = parser.add_argument_group("📄 Chapter Scraping")
    chapter_group.add_argument('--curl', '-c', type=str, help="🔗 Chapter URL to scrape.")

    # 🔍 Search
    search_group = parser.add_argument_group("🔍 Search")
    search_group.add_argument('--search', '-f', type=str, help="🔎 Search manga.")
    search_group.add_argument('--host', '-hs', type=str, help="🌐 Website for search.")

    # ⚡ Debugging
    debug_group = parser.add_argument_group("⚡ Debugging & Logging")
    debug_group.add_argument('--savejson', '-j', action='store_true', help="💾 Save data as JSON.")
    debug_group.add_argument('--debug', '-d', action='store_true', help="🐞 Enable debug mode.")
    debug_group.add_argument('--log', '-l', action='store_true', help="📝 Save logs.")
    debug_group.add_argument('--update', '-u', action='store_true', help="🔄 Update saved data.")

    args = parser.parse_args()

    # 🛠 Handle Arguments
    if args.murl:
        return (args.murl, args.start, args.end, args.output or os.getcwd(), args.workthreads or 1, args.imagethreads or 1, args.listchapter, args.nocover, args.debug, args.savejson, args.update, args.log)

    if args.curl:
        return (args.curl, args.output or os.getcwd(), args.imagethreads or 1, args.debug, args.log)

    if args.search:
        return (args.search, args.host, args.debug, args.log)

    exit(1)

if __name__ == "__main__":
    getarr = arr()

    if len(getarr) == 12:  # Series scraping with all debug options
        (manga_url, start, end, output, workthreads, imagethreads, listchapter, nocover, debug, savejson, update, log) = getarr
        print(f'============================== CONFIG ==========================')
        print(f"Processing Series: {manga_url}...")
        print(f"Start: {start}, End: {end}")
        print(f"Output: {output}")
        print(f"Download Cover: {False if nocover else True}")
        print(f"Work Threads: {workthreads}")
        print(f"Image Threads: {imagethreads}")
        print(f"List Chapters: {listchapter}")
        print(f"Debug: {debug}")
        print(f"Save JSON: {savejson}")
        print(f"Update: {update}")
        print(f"Log: {log}\n")
        series.fetchInfo(manga_url, start, end, output, workthreads, imagethreads, listchapter, nocover, debug, savejson, update, log)
    elif len(getarr) == 6:  # Chapter scraping
        chapter_url, output, imagethreads, debug, log = getarr
        print(f'============================== CONFIG ==========================')
        print(f"Processing Chapter: {chapter_url}...")
        print(f"Output: {output}")
        print(f"Image Threads: {imagethreads}")
        print(f"Debug: {debug}")
        print(f"Log: {log}\n")
    elif len(getarr) == 5:  # Search
        search, host, debug, log = getarr
        print(f'============================== CONFIG ==========================')
        print(f"Searching for: {search} on {host}...")
        print(f"Debug: {debug}")
        print(f"Log: {log}\n")
    else:
        exit(1)