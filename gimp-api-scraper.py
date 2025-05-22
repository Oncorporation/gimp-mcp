import time
import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://developer.gimp.org/api/3.0/libgimp/"
PRIMITIVE_MAP = {
    "gchar": "string",
    "gboolean": "boolean",
    "gdouble": "number",
    "gfloat": "number",
    "gulong": "integer",
    "gint": "integer",
    "guint": "integer",
    "gsize": "integer",
    "gint*": "integer",
    "gchar*": "string",
    "gdouble*": "number",
    "gsize*": "integer",
    "gboolean*": "boolean",
    "gchar**": "string",
    "guint8*": "integer",
}

def glib_to_openapi(glib_type):
    # remove const
    glib_type = glib_type.replace("const ", "")
    if glib_type in PRIMITIVE_MAP:
        return PRIMITIVE_MAP[glib_type]
    return glib_type

def get_soup(driver, url):
    driver.get(url)
    time.sleep(1)  # Wait for JS to load
    return BeautifulSoup(driver.page_source, "html.parser")

def scrape_classes(driver):
    soup = get_soup(driver, BASE_URL)
    classes_section = soup.find("h4", id="classes")
    table = classes_section.find_next("div").find("table")
    paths = {}
    for row in table.find_all("tr")[1:]:
        a = row.find("a")
        class_name = a.text.strip()
        if class_name.startswith("Param"):
            continue
        class_url = urljoin(BASE_URL, a['href'])
        paths.update(scrape_class_methods(driver, class_name, class_url))
    return paths

def scrape_class_methods(driver, class_name, class_url):
    soup = get_soup(driver, class_url)
    sidebar = soup.find("nav", class_="sidebar")
    method_links = [a for a in sidebar.find_all("a") if "method" in a.get("href", "")]
    paths = {}
    for a in method_links:
        method_url = urljoin(class_url, a['href'])
        method_name = a.text.strip()
        method_data = scrape_method(driver, method_url)
        path = f"Gimp.{class_name}.{method_name}"
        paths[path] = {
            "get": {
                "summary": method_data["description"],
                "parameters": method_data["parameters"]
            }
        }
    return paths

def scrape_method(driver, method_url):
    soup = get_soup(driver, method_url)
    desc = soup.find("h4", id="description").find_next("p").text.strip()
    params = []
    params_dl = soup.find("h4", id="parameters")
    if params_dl:
        dl = params_dl.find_next("dl")
        for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
            method_desc = "No description available."
            if len(dd.find_all("p")) >= 3:
                method_desc = dd.find_all("p")[2].text.strip()
            is_required = dd.find("code", string="NULL") is None
            params.append({
                "name": dt.text.strip(),
                "in": "query",
                "description": method_desc,
                "required": is_required,
                "schema": {"type": glib_to_openapi(dd.find_all("p")[0].find("code").text.strip())}
            })
    return {"description": desc, "parameters": params}

def scrape_enums(driver):
    soup = get_soup(driver, BASE_URL)
    enums_section = soup.find("h4", id="enums")
    table = enums_section.find_next("div").find("table")
    enums = {}
    for row in table.find_all("tr")[1:]:
        a = row.find("a")
        enum_url = urljoin(BASE_URL, a['href'])
        enum_data = scrape_enum(driver, enum_url)
        enums[enum_data["name"]] = enum_data
    return enums

def scrape_enum(driver, enum_url):
    soup = get_soup(driver, enum_url)
    name = "Gimp." + soup.find("h1").text.strip()
    desc = soup.find("h4", id="description").find_next("div").find("p").text.strip()
    members = []
    members_table = soup.find("h4", id="members").find_next("div").find("table")
    for row in members_table.find_all("tr")[1:]:
        members.append(row.find_all("td")[0].text.strip())
    return {"name": name, "description": desc, "values": members}

def main():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    try:
        paths = scrape_classes(driver)
        enums = scrape_enums(driver)
        openapi = {
            "openapi": "3.0.0",
            "info": {"title": "GIMP 3.0 API", "version": "1.0.0"},
            "paths": paths,
            "components": {
                "schemas": {e["name"]: {"type": "string", "enum": e["values"], "description": e["description"]} for e in enums.values()}
            }
        }
        with open("gimp_openapi.yaml", "w") as f:
            yaml.dump(openapi, f)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()