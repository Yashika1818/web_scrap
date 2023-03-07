import deepchem as dc
from deepchem.models import GraphConvModel
import pubchempy as pcp
import numpy as np
import pandas as pd
from rdkit import Chem
import requests, json

def get_compound_url(compound_name):
    # fetch PubChem CID for the given compound name
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{compound_name}/cids/JSON"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content)
        if "IdentifierList" in data:
            cid = data["IdentifierList"]["CID"][0]
            return f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}"
        else:
            return f"https://pubchem.ncbi.nlm.nih.gov/"
    else:
      return f"https://pubchem.ncbi.nlm.nih.gov/"
    

tox21_tasks = ['NR-AR',
 'NR-AR-LBD',
 'NR-AhR',
 'NR-Aromatase',
 'NR-ER',
 'NR-ER-LBD',
 'NR-PPAR-gamma',
 'SR-ARE',
 'SR-ATAD5',
 'SR-HSE',
 'SR-MMP',
 'SR-p53']


model = dc.models.GraphConvModel(len(tox21_tasks), mode='classification', model_dir='tox_pred')
model.restore()

environment_task = ['NR-AhR', 'NR-PPAR-gamma', 'SR-ARE', 'SR-ATAD5', 'SR-HSE', 'SR-MMP', 'SR-p53']
aquatic_task = ['NR-Aromatase', 'NR-ER', 'NR-ER-LBD', 'NR-PPAR-gamma', 'SR-ARE', 'SR-ATAD5', 'SR-HSE', 'SR-MMP']

environment_task_indices = [tox21_tasks.index(task) for task in environment_task]
aquatic_task_indices = [tox21_tasks.index(task) for task in aquatic_task]

def predict_toxicity(compound):
    featurizer = dc.feat.graph_features.ConvMolFeaturizer()
    features = featurizer([compound])
    composite_preds =  model.predict_on_batch(features)[0]
    environment_preds = composite_preds[environment_task_indices]
    aquatic_preds = composite_preds[aquatic_task_indices]
    return environment_preds, aquatic_preds, composite_preds

# def get_ingredients_from_product(product):
#    return """Water, Glycerin, Propylene glycol, Glyceryl stearate, Cetyl alcohol, Stearyl alcohol, Dimethicone, Cyclomethicone""".lower().split(", ")
# ings = get_ingredients_from_product()

def generate_ings_exempts(ings):
    list_of_ingredients = set(ings)
    exemptions = set(['water', 'salt', 'sugar', 'malic acid', 'colour', 'paprika' ,'sodium chloride', 'potassium chloride', 'magnesium chloride', 'calcium chloride', 'sodium hydroxide', 'potassium hydroxide', 'ammonium hydroxide', 'hydrochloric acid', 'sulfuric acid', 'nitric acid', 'acetic acid', 'citric acid', 'lactic acid', 'benzoic acid', 'salicylic acid', 'urea', 'glycerin', 'propylene glycol', 'ethanol', 'isopropyl alcohol', 'hexylene glycol', 'butylene glycol', 'propanediol', 'polyethylene glycol (PEG)', 'sorbitol', 'xylitol', 'sucralose', 'saccharin', 'aspartame', 'titanium dioxide', 'iron oxide'])
    ingredients = list(list_of_ingredients - exemptions)
    exempts = list(list_of_ingredients - set(ingredients))
    return ingredients, exempts

def get_compounds(ingredients):
    compounds = {}
    for ingredient_name in ingredients:
        try:
            result = pcp.get_compounds(ingredient_name, 'name')[0]
            compound = Chem.MolFromSmiles(result.canonical_smiles)
            compounds[compound] = ingredient_name
        except:
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{ingredient_name}/cids/JSON"
            response = requests.get(url)
            if response.status_code == 200:
                data = json.loads(response.content)
                if "IdentifierList" in data:
                    cid = data["IdentifierList"]["CID"][0]
                    tox_request_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/2286/JSON?cid={}".format(cid)
                    tox_response = requests.get(tox_request_url)
                    tox_data = json.loads(tox_response.text)
                    print(tox_data)
                else:
                    print("Left:", ingredient_name)
            else:
                print("Left:", ingredient_name)
    return compounds

def get_summary(compounds, exempts):
    summary = {}
    overall = 0
    ingredient_count = len(compounds) + len(exempts)
    aqua_tot, env_tot = 0, 0
    for compound, name in compounds.items():
        environment_preds, aquatic_preds, composite_preds = predict_toxicity(compound)
        env, aqua, comp = environment_preds.mean(axis=0)[0], aquatic_preds.mean(axis=0)[0], composite_preds.mean(axis=0)[0]
        overall += comp
        aqua_tot += aqua
        env_tot += env
        summary[name.capitalize()] = [str(aqua), str(env), get_compound_url(name)]
    summary["Overall"] = str(overall / ingredient_count)
    summary["Aquatic"] = str(aqua_tot / ingredient_count)
    summary["Environment"] = str(env_tot / ingredient_count)
    for ing in exempts:
        summary[ing.capitalize()] = ['0', '0', get_compound_url(ing)]
    return summary