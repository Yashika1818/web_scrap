from flask import Flask, request, jsonify
import requests
from model import *
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route("/cosmetics", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        product = request.form.get("product_name")
        if product is None:
            return "product name not found"
        # cosmetics
        url = "https://incidecoder.com/"
        res = requests.get(url + "search?query={}".format(product))
        soup_data = BeautifulSoup(res.text, "html.parser")

        links = soup_data.find_all("a", class_="klavika simpletextlistitem")
        specific = links[0]["href"]

        details = requests.get(url + specific[1:])
        soup = BeautifulSoup(details.text, "html.parser")
        all_ing = set()
        for li in soup.find_all("a", class_="ingred-link black"):
            all_ing.add(li.text.lower())
        ingredients, exempts = generate_ings_exempts(list(all_ing))
        summary = get_summary(get_compounds(ingredients), exempts)
        return jsonify(summary)



@app.route("/food", methods=["GET", "POST"])
def data():
    if request.method == "POST":
        product = request.form.get("product_name")
        if product is None:
            return "product name not found"
        # food
        url = "https://in.openfoodfacts.org/"
        x = product.split()
        after_join = "+".join(x)
        url2 = (
            url
            + "cgi/search.pl?search_terms={}".format(after_join)
            + "&search_simple=1&action=process"
        )
        r = requests.get(url2)
        htmlContent = r.text
        soup = BeautifulSoup(htmlContent, "html.parser")

        links = soup.find("ul", class_="products")
        ingredients = None
        while ingredients == None:
            link = links.find_all("li")[i]
            anchors = link.find("a")
            specific = anchors["href"]
            details = requests.get(url + specific[1:])
            soup = BeautifulSoup(details.text, "html.parser")
            ingredients = soup.find("ol", id="ordered_ingredients_list")

        all_ing = set()
        for li in ingredients.find_all("span"):
            all_ing.add(li.text.lower())
        
        ingredients, exempts = generate_ings_exempts(list(all_ing))
        summary = get_summary(get_compounds(ingredients), exempts)
        return jsonify(summary)


if __name__ == "__main__":
    app.run(debug=True)
