from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time
import io

driver = webdriver.Chrome('chromedriver.exe')
driver.get("https://offcampus.mcmaster.ca/available-properties/")

# login
userInput = driver.find_elements_by_css_selector('form input')[1]
passwordInput = driver.find_elements_by_css_selector('form input')[2]

userInput.send_keys("")
passwordInput.send_keys("")
passwordInput.send_keys(Keys.ENTER)
time.sleep(12)

json = []
thumbnails = list(map(lambda x: x.find_element_by_css_selector(".d-sm-none.d-md-block.card-img-mask.card-img-mask-top").find_element_by_tag_name("img").get_attribute("src"), driver.find_elements_by_css_selector(".col-lg-3.col-md-6.col-sm-12.list-item")))
listings = list(map(lambda x: x.find_element_by_tag_name("a").get_attribute("href"), driver.find_elements_by_css_selector(".col-lg-3.col-md-6.col-sm-12.list-item")))

for i, listing in enumerate(listings):
    driver.get(listing)

    d = {}

    # THUMBNAIL
    d["thumbnail"] = thumbnails[i]

    # TITLE
    d["title"] = driver.find_element_by_css_selector(".mb-4").text

    # DESCRIPTION
    d["description"] = driver.find_element_by_css_selector(".light-grey.mb-0.p-lg-4.p-2").find_element_by_tag_name("p").text

    # DETAILS
    labels = {"property type": "propertyType", "rent per month": "rent", "# of bedrooms available": "bedroomsAvailable", "# of bedrooms in property": "bedroomsInProperty", "lease time": "leaseTime", "date available": "dateAvailable"}
    t = {"propertyType": "", "rent": "", "bedroomsAvailable": "", "bedroomsInProperty": "", "leaseTime": "", "dateAvailable": ""}
    d["details"] = {labels[k.lower()]: v for k,v in list(map(lambda x: (x.find_element_by_tag_name("h2").text, x.find_element_by_tag_name("p").text), driver.find_elements_by_css_selector(".col-lg-auto.col-md-6.flex-fill")))}

    # AMENITIES UTILITIES
    d["amenities"] = []
    d["utilities"] = []
    for stuff in driver.find_elements_by_css_selector(".row.row-eq-height")[1].find_elements_by_css_selector(".col-md-6"):
        k = stuff.find_element_by_tag_name("h3").text.split()[0].lower()
        v = list(map(lambda x: x.text, stuff.find_elements_by_tag_name("li")))
        d[k] = v

    # CONTACT
    driver.find_element_by_css_selector(".btn.btn-primary.dropdown-toggle").click()

    temp = []
    try:
        temp.append(driver.find_element_by_css_selector(".dropdown-menu.show").find_element_by_tag_name("a").get_attribute("href")[5:])
    except NoSuchElementException:
        temp.append("")
    try:
        temp.append(driver.find_element_by_css_selector(".modal-footer").find_element_by_tag_name("input").get_attribute("value"))
    except NoSuchElementException:
        temp.append("")
    d["contact"] = {"phone": temp[0], "email": temp[1]}

    # IMAGES
    try:
        d["images"] = list(map(lambda x: x.get_attribute("href"), driver.find_element_by_css_selector(".flickity-slider").find_elements_by_tag_name("a")))
    except NoSuchElementException:
        d["images"] = []

    # LOCATION
    temp = []
    for location in driver.find_element_by_css_selector(".col-xl-9.col-lg-8.pt-5.pr-lg-5").find_element_by_css_selector(".py-4").find_element_by_css_selector(".col-12").find_elements_by_tag_name("option")[1:]:
        t = {
            "distance": location.get_attribute("data-distance"),
            "walkingTime": location.get_attribute("data-walking-time"),
            "drivingTime": location.get_attribute("data-driving-time"),
            "transitTime": location.get_attribute("data-transit-time")
        }
        temp.append(t)
    d["location"] = {
        "l1": temp[0],
        "l2": temp[1],
        "l3": temp[2],
        "l4": temp[3],
        "l5": temp[4],
        "l6": temp[5]
    }

    # MAP
    d["map"] = driver.find_element_by_tag_name("iframe").get_attribute("data-src")

    json.append(d)
    print(d)
    print()


f = io.open('output.txt', 'w', encoding="utf-8")
f.write(str(json))
f.close()
