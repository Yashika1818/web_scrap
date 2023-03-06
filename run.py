from flask import Flask,request, jsonify
import requests
from bs4 import BeautifulSoup
app= Flask(__name__)

@app.route("/cosmetics",methods=['GET','POST'])
def home():
    text=0
    total=0
    if request.method == 'POST':
        # text = str(request.args["product_name"])
        text= request.form.get('product_name')
        if text is None:
            return "product name not found …"


# cosmetics

        url = "https://incidecoder.com/"
        

        res = requests.get(url+'search?query={}'.format(text))
        soup_data = BeautifulSoup(res.text, 'html.parser')

        links = soup_data.find_all('a', class_="klavika simpletextlistitem")
        specific = links[0]["href"]

        details = requests.get(url + specific[1:])
        soup = BeautifulSoup(details.text, 'html.parser')
   
        # ingredients = soup.find_all('a', class_="ingred-link black")
        all_ing=set()
        for li in soup.find_all('a', class_="ingred-link black"):
            all_ing.add(li.text)
        print(all_ing)
        # print(ingredients)

        total=30
        return jsonify({"product":text,"prediction": total})
    


@app.route("/food",methods=['GET','POST'])
def data():
    text=0
    total=0
    if request.method == 'POST':
        # text = str(request.args["product_name"])
        text= request.form.get('product_name')
        if text is None:
            return "product name not found …"
# food
        url="https://in.openfoodfacts.org/"
        x=text.split()
        after_join='+'.join(x)
        # print(after_join)



        url2=url+"cgi/search.pl?search_terms={}".format(after_join)+"&search_simple=1&action=process"
        # print(url2)
        r=requests.get(url2)
        htmlContent=r.text
        soup=BeautifulSoup(htmlContent,'html.parser')

        links = soup.find('ul', class_="products")
        ingredients=None
        i=0
        while ingredients==None :
            link= links.find_all("li")[i]
            i+=1
            anchors=link.find('a')
        
            specific = anchors["href"]
        
            # print(url + specific[1:])
            details = requests.get(url + specific[1:])
            soup = BeautifulSoup(details.text, 'html.parser')
        
            ingredients = soup.find('ol', id="ordered_ingredients_list")
            # print(ingredients)

        all_ing=set()
        for li in ingredients.find_all("span"):
            all_ing.add(li.text)
        print(all_ing)
        total=30
        return jsonify({"product":text,"prediction": total})

if __name__ == '__main__':
    app.run(debug=True)
 

