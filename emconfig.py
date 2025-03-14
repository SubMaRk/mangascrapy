def config(section_id):
    """Returns the configuration for a given section ID."""
    if section_id == 1:
        return {
            "title": [
                "div.post-title-custom h1",
                "div.post-title h1",
                "div#manga-title h1"
            ],
            "type": [
                "Type",
                "ประเภท"
            ],
            "genre": [
                "Genre(s)",
                "ประเภทมังงะ",
                "หมวด",
                "หมวดหมู่"
            ],
            "status": [
                "Status",
                "สถานะ",
                "สถานะมังงะ"
            ],
            "chapterlist": [
                "div.listing-chapters_wrap ul li",
                "div#chapterlist ul li",
                "ul.main li",
                "ul#chapterList"
            ],
            "cover": ["div.summary_image a img"]
        }
    elif section_id in (2, 3, 4):
        return {
            "title": [
                "h1.entry-title",
                "div.series-title h2"
            ],
            "type": [
                "div.fmed:has(b:-soup-contains('ประเภทเรื่อง')) span",
                ".series-infoz .type",
                "td:has(> b:-soup-contains('Type')) + td",
                "span.btct.ct-type"
            ],
            "genre": [
                "div.wd-full span.mgen a",
                ".series-genres a",
                "div.seriestugenre a",
                "ul.mgen.genre li a"
            ],
            "status": [
                "div.fmed:has(b:-soup-contains('สถานะ')) i",
                ".series-infoz .status",
                "td:has(> b:-soup-contains('Status')) + td",
                "span.btct.ct-status"
            ],
            "chapterlist": [
                "div.eplister ul li",
                ".series-chapterlist li"
            ],
            "cover": [
                "div.thumb img",
                ".series-thumb img"
            ]
        }
