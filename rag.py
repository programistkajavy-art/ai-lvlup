from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)
from azure_client_factory import AzureClientFactory
from pathlib import Path
import json

class Rag:
    index_client = None
    search_client = None
    def __init__(self):
        try:
            self.index_client = AzureClientFactory.get_search_index_client()
            self.search_client = AzureClientFactory.get_search_client()
        except Exception as e:
            print(f"❌ BŁĄD połączenia: {e}\n")
            exit(1)

    def add_recipes(self):
        #self.create_recipes_index()
        folder = Path("recipes")

        recipes = []

        for file_path in folder.glob("*.json"):
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                recipes.extend(data)

        all_recipes = []

        for recipe in recipes:
            ingredients_full = "\n".join([f"{ing['amount']} {ing['name']}"  for ing in recipe['ingredients'] ])
            #print(f"ingredients_full:\n{ingredients_full}")

            ingredients_names = ", ".join([ing['name'] for ing in recipe['ingredients'] ])
            #print(f"ingredients_names:\n{ingredients_names}")

            instructions = "\n".join([f"{i+1}. {step}" for i, step in enumerate(recipe['instructions']) ])
            #print(f"instructions:\n{instructions}")
            
            one_recipes = {
                "id": str(recipe['lp']),
                "name": recipe['name'],
                "ingredients_full": ingredients_full,
                "ingredients_names": ingredients_names,
                "instructions": instructions
            }

            #print(f"one_recipes:\n{one_recipes}")

            all_recipes.append(one_recipes)

        try:
            result = self.search_client.upload_documents(documents=all_recipes)
            print(f"✅ Załadowano {len(all_recipes)} przepisów do Azure Search.")
            return result
        except Exception as e:
            print(f"❌ Błąd podczas ładowania przepisów: {e}")
            return None    

            # print(f"Wczytano {len(recipes)} przepisów.")

        # print (f"{recipes}")

    def create_recipes_index(self):
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="name", type=SearchFieldDataType.String),
            SearchableField(name="ingredients_full", type=SearchFieldDataType.String),
            SearchableField(name="ingredients_names", type=SearchFieldDataType.String),
            SearchableField(name="instructions", type=SearchFieldDataType.String)
        ]
        
        index = SearchIndex(name=AzureClientFactory.INDEX, fields=fields)
        
        try:
            self.index_client.create_index(index)
            print(f"✅ Indeks '{AzureClientFactory.INDEX}' został utworzony.")
        except Exception as e:
            print(f"ℹ️  Indeks już istnieje lub błąd: {e}")


if __name__ == "__main__":
     rag = Rag()
     #NIe trzeba już uruchamiac, zrobiłam i dodałam index i przepisy, fajnie działa :D
     #rag.add_recipes()
