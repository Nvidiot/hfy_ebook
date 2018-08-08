import praw
import requests

from lxml import etree

REDDIT_CLIENT_ID='CLIENT_ID_HERE'
REDDIT_CLIENT_SECRET='SECRET_HERE'
REDDIT_CLIENT_UA='linux:hfy_ebook_creator:v0.0.1 (by /u/Nv1diot)'
REDDIT = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                     client_secret=REDDIT_CLIENT_SECRET,
                     user_agent=REDDIT_CLIENT_UA)


class Chapter(object):
    author = None
    series = None
    title = None
    url = None

    def __repr__(self):
        return "Chapter(author='%s', series='%s', title='%s', url='%s')" % (self.author, self.series, self.title, self.url)


def get_hfy_etree():
    hfy_all_html = REDDIT.subreddit('hfy').wiki['ref/universes/jenkinsverse/all_works'].content_html
    hfy_all_html = hfy_all_html.replace(u'\u2019', u"'")
    hfy_all_html = hfy_all_html.replace(u'\u2013', u"-")
    return etree.fromstring(hfy_all_html)


tree = get_hfy_etree()
all_chapters = []
# get all links that are bold (canon works only)
for link in tree.xpath("//div[contains(@class, 'wiki')]/ul/li/strong"):
    c = Chapter()

    a_tag = link.xpath('.//a')[0]
    c.title = a_tag.text
    c.url = a_tag.attrib['href']
    if link.text:
        c.title = link.text + c.title

    all_chapters.append(c)

for c in all_chapters:
    # Detect correct series per chapter
    if 'Kevin Jenkins Experience' in c.title:
        c.series = 'The Deathworlders'
    if c.title[0].isdigit():
        c.series = "The Deathworlders"
    if "Humans don't Make Good Pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans don't Make Good Pets ", "")
    if "Humans don't make good pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans don't make good pets ", "")
    if "Humans Don't Make Good Pets" in c.title:
        c.series = "Humans don't Make Good Pets"
        c.title = c.title.replace("Humans Don't Make Good Pets ", "")
    if "The Lost Minstrel" in c.title:
        c.series = "The Lost Minstrel"
        c.title = c.title.replace("The Lost Minstrel - ", "")
    if c.title.startswith('MIA'):
        c.series = "MIA"
        c.title = c.title.replace("MIA - ", "")
        c.title = c.title.replace("MIA ", "")
    if "Deathworld Origins" in c.title:
        c.series = "Deathworld Origins"
        c.title = c.title.replace("Deathworld Origins: ", "")
    if "Salvage - " in c.title:
        c.series = "Salvage"
        c.title = c.title.replace("Salvage - ", "")
    if "Salvage " in c.title:
        c.series = "Salvage"
        c.title = c.title.replace("Salvage ", "")
    if "Good Training" in c.title:
        c.series = "Good Training"
        c.title = c.title.replace("Good Training: ", "")
        if c.title == "":
            c.title = "0"
    if "Henosis " in c.title:
        c.series = "Henosis"
        c.title = c.title.replace("Henosis ", "")
    if "Monkeys Reaches Stars" in c.title:
        c.series = "Xiu Chang Saga"
    if "The Tiger's Cub" in c.title:
        c.series = "Xiu Chang Saga"
    if "Rat in Sheep's Clothing" in c.title:
        c.series = "Xiu Chang Saga"
    if "The Ox's Plan" in c.title:
        c.series = "Xiu Chang Saga"
    if "A Wounded Rabbit" in c.title:
        c.series = "Xiu Chang Saga"
    if "Waters of Babylon" in c.title:
        c.series = "Waters of Babylon"
        c.title = c.title.replace("Waters of Babylon - ", "")

    # Manually clean up some titles to match easier with Deathworlders website
    if c.title == "5.5: Interlude and Ultimatum":
        c.title = "5.5: Interlude/Ultimatum"
    if c.title == "21.5: d4 d5, c4 dxc4.":
        c.title = "Interlude/d4 d5, c4 dxc4"
    if c.title == "22.5: Outlets":
        c.title = "Interlude/Outlets"
    if "War on Two Worlds" in c.title:
        c.title = c.title.replace(" pt.1 - ", ", Part 1-")
        c.title = c.title.replace(" pt.2 - ", ", Part 2-")
        c.title = c.title.replace(" pt.3 - ", ", Part 3-")
        c.title = c.title.replace(" pt.4 - ", ", Part 4-")
        c.title = c.title.replace(" pt.5 - ", ", Part 5-")


    # Store reference to Deathworlders: Warhorse. This needs to be replaced by 6 new ones
    if c.title == "22: Warhorse" and c.series == "The Deathworlders":
        warhorse_chapter = c


# Remove art links
to_remove = []
for c in all_chapters:
    if 'Concept Art' in c.title:
        to_remove.append(c)
for c in to_remove:
    all_chapters.remove(c)


# Fetch all Deathworlders titles + series
deathworlders = []
for i in range(1,11):
    #FIXME: auto-detect how many pages there are
    if i == 1:
        page = requests.get('https://deathworlders.com/')
    else:
        page = requests.get('https://deathworlders.com/page/' + str(i) + '/')

    page_text = page.text
    page_text = page_text.replace(u"\u2014", "-")
    page_text = page_text.replace(u"\u2019", "'")

    tree = etree.HTML(page_text)
    for a_tag in tree.xpath("//main/section/ul/li/a"):
        c = Chapter()
        c.series = a_tag.text
        c.title = a_tag.getchildren()[0].tail.replace(u"\u2019", "'")
        c.url = 'https://deathworlders.com' + a_tag.attrib['href']
        deathworlders.append(c)


# Splice in Warhorse chapters
warhorse_chapters_dw = []
for c in deathworlders:
    if c.series == "The Deathworlders" and 'Warhorse' in c.title:
        warhorse_chapters_dw.append(c)
warhorse_chapters_dw.reverse()
loc = all_chapters.index(warhorse_chapter)
all_chapters = all_chapters[0:loc] + warhorse_chapters_dw + all_chapters[loc+1:]

for c in all_chapters:
    if c.series == 'The Deathworlders':
        for dw in deathworlders:
            if dw.series == 'The Deathworlders':
                dw_title = dw.title.split(":", 1)[1].strip()
                if dw_title.lower() in c.title.lower():
                    c.url = dw.url
    if c.series == "Waters of Babylon":
        c.title = c.title.replace(".", "")
        for dw in deathworlders:
            if dw.series == "Waters of babylon":
                # No capital 'b' in Deathworlders site
                if dw.title.lower() in c.title.lower():
                    c.url = dw.url


# First part of 'Good Training'
for c in all_chapters:
    if c.series == "Good Training" and c.title == "Good Training":
        gt = c
gt_chapters_dw = []
for c in deathworlders:
    if c.series == "Good Training" and "Chapter" in c.title:
        gt_chapters_dw.append(c)
loc = all_chapters.index(gt)
all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]

# Good Training: The Champions
for c in all_chapters:
    if c.series == "Good Training" and c.title == "The Champions":
        gt = c
gt_chapters_dw = []
for c in deathworlders:
    if c.series == "Good Training: the Champions Part I":
        gt_chapters_dw.append(c)
loc = all_chapters.index(gt)
all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]

# Good Training: The Champions part 2
for c in all_chapters:
    if c.series == "Good Training" and c.title == "The Champions Part 2":
        gt = c
gt_chapters_dw = []
for c in deathworlders:
    if c.series == "Good Training: the Champions Part II":
        gt_chapters_dw.append(c)
loc = all_chapters.index(gt)
all_chapters = all_chapters[0:loc] + gt_chapters_dw + all_chapters[loc+1:]

# Deathworld Origins
for c in all_chapters:
    if c.series == "Deathworld Origins":
        c.url = "https://captainmeta4.me/books/deathworld_origins/" + c.title

# Filter duplicate urls
prev_url = None
to_delete = []
for c in all_chapters:
    if prev_url and c.url == prev_url:
        to_delete.append(c)
    prev_url = c.url
for c in to_delete:
    all_chapters.remove(c)


# Make sure to have no None values for series:
for c in all_chapters:
    if c.title == "The Brink":
        c.series = "The Brink"
    if c.title == "The Catechism of the Gricka":
        c.series = "The Catechism of the Gricka"


# Set authors
for c in all_chapters:
    if c.series == "The Deathworlders":
        c.author = "Hambone"
    elif c.series == "Humans don't Make Good Pets":
        c.author = "guidosbestfriend"
    elif c.series == "Xiu Chang Saga":
        c.author = "hume_reddit"
    elif c.series == "Salvage":
        c.author = "Rantarian"
    elif c.series == "MIA":
        c.author = "GoingAnywhereButHere"
    elif c.series == "Henosis":
        c.author = "hume_reddit"
    elif c.series == "The Lost Minstrel":
        c.author = "doules1071"
    elif c.series == "Good Training":
        c.author = "ctwelve"
    elif c.series == "Good Training: the Champions Part I":
        c.author = "ctwelve"
    elif c.series == "Good Training: the Champions Part II":
        c.author = "ctwelve"
    elif c.series == "Deathworld Origins":
        c.author = "captainmeta4"
    elif c.series == "The Brink":
        c.author = "slice_of_pi"
    elif c.series == "Waters of Babylon":
        c.author = "slice_of_pi"
    elif c.series == "The Catechism of the Gricka":
        c.author = "slice_of_pi"

        
# Create spec file
header = \
"""{
    "title": "Humanity - Fuck Yeah! - Canon",
    "creator": "Hambone, guidosbestfriend, hume_reddit, Rantarian, GoingAnywhereButHere, doules1071, ctwelve, slice_of_pi, captainmeta4",
    "filters": {
        "reddit": [
            "from-reddit-post",
            "clean-reddit",
            "custom-break-to-hr",
            "no-preamble",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "hfy-archive": [
            "from-hfy-archive",
            "clean-reddit",
            "custom-break-to-hr",
            "no-preamble",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "deathworld-origins": [
            "from-deathworld-origins",
            "clean-reddit",
            "custom-break-to-hr",
            "jverse-the-deathworlders",
            "typography",
            "finalize"
        ],
        "humans-pets": [
                "from-reddit-post",
                "clean-reddit",
                "no-preamble",
                "jverse-hdmgp",
                "typography",
                "finalize"
        ],
        "mia": [
                "from-reddit-post",
                "clean-reddit",
                "no-preamble",
                "jverse-mia",
                "typography",
                "finalize"
        ],
        "salvage": [
                "from-reddit-post",
                "clean-reddit",
                "custom-break-to-hr",
                "no-preamble",
                "jverse-salvage",
                "typography",
                "finalize"
        ],
        "xiu": [
                "from-reddit-post",
                "clean-reddit", 
                "no-preamble",
                "jverse-txcs",
                "typography",
                "finalize"
        ]
    },
    "filename": "Humanity - Fuck Yeah - Canon",
    "output": ["epub", "latex", "html"],
    "contents":
    [
"""

footer = \
"""
    ]
}
"""

spec_chapter = \
"""
        {
            "title": "%s",
            "filters": "%s",
            "src": "%s"
        }
"""

spec_file = open('HFY_Canon.spec', 'w')
spec_file.write(header)
chapter_list = []
for c in all_chapters:
    if 'deathworlders.com' in c.url:
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "hfy-archive", c.url))
    elif c.series == "Humans don't Make Good Pets":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "humans-pets", c.url))
    elif c.series == "MIA":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "mia", c.url))
    elif c.series == "Salvage":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "salvage", c.url))
    elif c.series == "Xiu Chang Saga":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "xiu", c.url))
    elif c.series == "Deathworld Origins":
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "deathworld-origins", c.url))
    else:
        chapter_list.append(spec_chapter % (c.series + ": " + c.title, "reddit", c.url))

spec_file.write(",\n".join(chapter_list))
spec_file.write(footer)
spec_file.close()

