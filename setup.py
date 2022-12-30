# use sqlalchemy to setup the pap database
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import Tables
import random
import os
import re
import pydantic
from typing import List
import pickle
import requests
import bs4


class President(pydantic.BaseModel):
    president_id: int
    name: str
    image: str


class Quiz(pydantic.BaseModel):
    id: int
    quote: str
    correct_answer: str
    choices: List[str]

def create_quiz(quote: str, correct_answer: Tables.President):
    choices = set([correct_answer.name])
    while len(choices) < 4:
        choices.add(random.choice(all_presidents).name)
    choices = list(choices)

    sess = sessionmaker(bind=engine)()

    quiz = Tables.Quiz(
        quote=quote,
        correct_answer=correct_answer.name,
        choices=",".join(choices),
    )

    sess.add(quiz)
    sess.commit()

    result = Quiz(
        id=quiz.id,
        quote=quiz.quote,
        correct_answer=quiz.correct_answer,
        choices=[c for c in choices],
    )
    
    sess.close()

    return result


def get_page(page):
    page = requests.get(page)
    return bs4.BeautifulSoup(page.text, "html.parser")


def extract_quotes(soup):
    """
    Find a div with class "mw-parser-output".
    Find an h2 with the text "Quotes"
    Find all ul tags between that h2 and the next h2
    Add the first li text to quotes for each ul.

    """
    quotes = []
    div = soup.find("div", {"class": "mw-parser-output"})
    uls = []
    collect = False
    for tag in div.children:
        if tag.name == "h2":
            if tag.text == "Quotes[edit]" or tag.text == "Quotes":
                collect = True
            else:
                collect = False
        if collect and tag.name == "ul":
            uls.append(tag)

    for ul in uls:
        quotes.append(ul.find("li").text)


    return quotes


def create_quizes(quotes, president_name):
    quizes = []

    for quote in quotes:
        quote = quote.split("\n")[0].strip()

        q = create_quiz(
            quote=quote,
            correct_answer=president_name
        )

        print("Quiz created.", q)





fns = os.listdir("./images")
fns = [fn for fn in fns if re.match(r"\d+", fn)]

engine = create_engine("sqlite:///pap.db")
Tables.Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

pres_list = """41,George H. W. Bush
09,William Henry Harrison
33,Harry S. Truman
22,Grover Cleveland
42,Bill Clinton
05,James Monroe
21,Chester A. Arthur
20,James A. Garfield
10,John Tyler
31,Herbert Hoover
30,Calvin Coolidge
32,Franklin D. Roosevelt
04,James Madison
07,Andrew Jackson
35,John F. Kennedy
29,Warren G. Harding
37,Richard Nixon
13,Millard Fillmore
40,Ronald Reagan
23,Benjamin Harrison
01,George Washington
28,Woodrow Wilson
02,John Adams
12,Zachary Taylor
26,Theodore Roosevelt
06,John Quincy Adams
03,Thomas Jefferson
45,Donald Trump
18,Ulysses S. Grant
34,Dwight D. Eisenhower
44,Barack Obama
27,William Howard Taft
43,George W. Bush
15,James Buchanan
25,William McKinley
14,Franklin Pierce
19,Rutherford B. Hayes
46,Joe Biden
16,Abraham Lincoln
17,Andrew Johnson
11,James K. Polk
08,Martin Van Buren
36,Lyndon B. Johnson
38,Gerald R. Ford
39,Jimmy Carter"""

pres_list = pres_list.splitlines()

presidents = []
for i in range(len(fns)):
    imageSrc = fns[i]
    id, name = pres_list[i].split(",")
    
    pres = Tables.President(id=id, name=name, image=imageSrc)
    presidents.append(pres)

sess = sessionmaker(bind=engine)()
sess.add_all(presidents)
sess.commit()
sess.close()


all_presidents = [President(president_id=p.id, name=p.name, image=p.image) for p in sess.query(Tables.President).all()]

plist = []
for p in pres_list:
    _, name = p.split(",")
    plist.append(name)

pages = {
    pres: f"https://en.wikiquote.org/wiki/{pres.replace(' ', '_')}"
    for pres in plist
}

html_pages = {pres: get_page(page) for pres, page in pages.items()}

for key in html_pages:
    with open(f"Quotes/{key}.html", "w") as f:
        f.write(str(html_pages[key]))


# load the html pages
html_pages = {}
for fn in os.listdir("Quotes"):
    with open(f"Quotes/{fn}", "r") as f:
        html_pages[fn[:-5]] = bs4.BeautifulSoup(f.read(), "html.parser")


presidents = {
    n.name.replace(" ", "_"): n
    for n in all_presidents
}

pquotes = {}
for pname, pres in presidents.items():
    qs = extract_quotes(html_pages[pres.name])
    pquotes[pres.name] = qs


for key in pquotes:
    random.shuffle(pquotes[key])

pquotes = {
    pres: [q for q in qs if 10 < len(q) < 300][:10]
    for pres, qs in pquotes.items()
}

for name, qs in pquotes.items():
    create_quizes(qs, presidents[name.replace(" ", "_")])

