# 📖 Manga Scraper CLI

## Description
Manga Scraper CLI is a command-line tool designed to download manga series, individual chapters, or search for manga across different websites. It provides multithreading support for improved performance and customizable options for efficient scraping.

---

## Supported Websites
All supported sites use templates from:
- [Themesia](https://themesia.com/)
- [Mangabooth](https://mangabooth.com/)

---

## Bugs
Currently, encrypted images on reading pages are unsupported.

---

## 🔹 Features
- 📚 Download complete manga series by specifying a range of chapters.
- 📄 Download individual chapters from a given URL.
- 🔍 Search for manga on supported websites.
- ⚙️ Multithreading support for faster downloads.
- 📝 JSON logging and debugging options.

---

## 🚀 Installation
Ensure you have Python installed, then install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔧 Usage

### 📚 Downloading a Manga Series
```bash
python script.py --murl "https://manga.com/series" --start 1 --end 10 --workthreads 4 --imagethreads 4 --output "C:\path"
```
Or using shorthand:
```bash
python script.py -m "https://manga.com/series" -s 1 -e 10 -wt 4 -it 4 -o "C:\path"
```

### 📄 Downloading a Single Chapter
```bash
python script.py --curl "https://manga.com/chapter" --imagethreads 4 --output "C:\path"
```
Or using shorthand:
```bash
python script.py -c "https://manga.com/chapter" -it 4 -o "C:\path"
```

### 🔍 Searching for a Manga
```bash
python script.py --search "One Piece" --host "manga-site.com"
```
Or using shorthand:
```bash
python script.py -f "One Piece" -hs "manga-site.com"
```

---

## ⚙️ Available Options

### 🔧 Common Options
| Argument | Shorthand | Description |
|----------|----------|-------------|
| `--output` | `-o` | 📁 Output path (default: current directory) |
| `--imagethreads` | `-it` | 📸 Threads for image downloads (default: 1) |
| `--workthreads` | `-wt` | ⚙️ Threads for processing (default: 1) |

### 📚 Series Scraping
| Argument | Shorthand | Description |
|----------|----------|-------------|
| `--murl` | `-m` | 🔗 URL of the manga series |
| `--listchapter` | `-lc` | 📜 List chapters without downloading |
| `--start` | `-s` | ⏳ Start chapter |
| `--end` | `-e` | ⏹️ End chapter |
| `--nocover` | `-nc` | ❌ Skip downloading the cover image |

### 📄 Chapter Scraping
| Argument | Shorthand | Description |
|----------|----------|-------------|
| `--curl` | `-c` | 🔗 URL of the chapter |

### 🔍 Search
| Argument | Shorthand | Description |
|----------|----------|-------------|
| `--search` | `-f` | 🔎 Search manga |
| `--host` | `-hs` | 🌐 Website for search |

### ⚡ Debugging & Logging
| Argument | Shorthand | Description |
|----------|----------|-------------|
| `--savejson` | `-j` | 💾 Save scraped data as JSON |
| `--debug` | `-d` | 🐞 Enable debug mode |
| `--log` | `-l` | 📝 Save logs |
| `--update` | `-u` | 🔄 Update saved data |

---

## 🛠 Example Configurations

### Series Download Configuration
```
============================== CONFIG ==========================
Processing Series: https://manga.com/series...
Start: 1, End: 10
Output: /path
Download Cover: True
Work Threads: 4
Image Threads: 4
List Chapters: False
Debug: False
Save JSON: False
Update: False
Log: False
```

### Chapter Download Configuration
```
============================== CONFIG ==========================
Processing Chapter: https://manga.com/chapter...
Output: /path
Image Threads: 4
Debug: False
Log: False
```

### Search Configuration
```
============================== CONFIG ==========================
Searching for: One Piece on manga-site.com...
Debug: False
Log: False
```

---

## 💡 Notes
- Ensure website permissions before scraping to comply with terms of service.

---

## 📜 License
This project is licensed under the MIT License.

---

## 🤝 Contributing
Pull requests are welcome! If you have suggestions, feel free to open an issue.

