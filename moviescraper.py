from bs4 import BeautifulSoup
import urllib.request
import pymongo

movies = []


def get_page(n):
    source = urllib.request.urlopen(
        "https://www.imdb.com/search/title/?groups=top_1000&sort=user_rating,desc&count=100&start=" + str(
            n) + "&ref_=adv_nxt").read()
    html = BeautifulSoup(source, "html.parser")

    for x in html.find_all("div", class_="lister-item mode-advanced"):
        title = x.find("h3", class_="lister-item-header").find("a").text
        year = x.find("span", class_="lister-item-year text-muted unbold").text[
               -5:-1]
        rating = x.find("strong").text
        movies.append((year, rating, title))


for i in range(0, 10):
    get_page(i * 100 + 1)

movies.sort(reverse=True)

d = {}
for x in movies:
    y, r, t = x
    d[y] = d.get(y, []) + [t + " - " + r]

json = []
for k, v in d.items():
    json.append({"year": k, "movies": v})

client = pymongo.MongoClient(
    "mongodb+srv://th:th@cluster0-mselt.mongodb.net/db?retryWrites=true&w=majority")
db = client["db"]
col = db["movies"]
col.drop()
col.insert_many(json)

