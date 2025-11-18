from azure_client_factory import AzureClientFactory
import json

class GPTModel:
    client = None

    def __init__(self):
        try:
            self.client = AzureClientFactory.get_azure_open_ai()
        except Exception as e:
            print(f"❌ BŁĄD połączenia: {e}\n")
            exit(1)

    def ask_chat(self, image_caption: str):
         
        is_food_on_photo_promnt = f"""
        Użytkownik wrzucił zdjęcie do analizy. 
        Analiza odbyła się za pomocą azure.ai.vision.imageanalysis.
        To jest wynik tej analizy:  {image_caption}

        Przeanalizuj ten wynik i odpowiedz na pytanie czy na zdjęciu jest produkt spożywczy. Jeżeli jest to produkt spożyczy, poszukaj dla niego następujące informacje:
        - Wartości odżywcze w 100g 
        - zalety
        - wady
        - rekomendacje dla produktu
        wypełnij nimi JSONa w postaci {GPTModel.json_schema}
        W polu product_name wpisz nazwę rozpoznanego produktu, zawsze w języki polskim
        W polu product_type wpisz Food, jeśli to produkt spożywczy. 
        Jeżeli analizując opis zdjęcia możesz jednoznacznie określić że produkt nie jest spożywczy i wiesz jak się nazywa uzupełnij pole product_name a polu product_type wpisz NoFood
        Jeżeli analizując opis zdjęcia nie możesz jednoznacznie określić jaki produkt nie spożywczy (np. etykieta, pudełko z napisami, Torba z jedzeniem ale nie wiesz jakim dokładnie) nieuzupełniaj pola product_name, w polu product_type wpisz NoFood
        Nie uzupełniaj pola ingredients
        Odpowiedz tylko jsonem
        """
        try:
            response = self.client.chat.completions.create(
                model=AzureClientFactory.CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "Jesteś ekspertem identyfikacji produktów spożywczych w tekstach. Odpowiadaj jsonem"
                    },
                    {
                        "role": "user",
                        "content": is_food_on_photo_promnt
                    }
                ],
                temperature=0.3  # Niska temperatura = bardziej obiektywna analiza
            )

            #print(f"Wynik:  {response.choices[0].message.content.strip()}")
            result = response.choices[0].message.content.strip()
            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[len("```json"):].strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            return cleaned

        except Exception as e:
                raise ValueError(f"❌ Błąd podczas analizy: {str(e)}")

    def get_recipes_from_rag(self,product_name):

        client = AzureClientFactory.get_search_client()          
        result_from_rag = client.search(
            search_text=product_name,
            top=5,
            select=["name", "ingredients_full", "ingredients_names", "instructions"]
        )      
        result_from_rag = list(result_from_rag)
        print(f"*********************** {result_from_rag}")
        prompt = f"""{result_from_rag}
            Na podstawieni powyższych przepisów wybierz 1, który zawiera składnik {product_name} i sformatuj go, żeby był czytelny dla użytkownika i gotowy do wyświetlenia w textBox. Jeżeli nie znajdziesz, napisz że nie masz i życzysz udanych eksperymentów w kuchni"""

        try:
            response = self.client.chat.completions.create(
                model=AzureClientFactory.CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "Jesteś pomocnym asystentem kulinarnym. Na podstawie dostarczonego kontekstu pomóż użytkownikowi znaleźć odpowiedni przepis. Odpowiadaj po polsku. Odpowiedź powinna być czytelna dla użytkownika i gotowa do wyświetlenia w textBox"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5  # Niska temperatura = bardziej obiektywna analiza
            )

            #print(f"Wynik:  {response.choices[0].message.content.strip()}")
            result = response.choices[0].message.content.strip()

            print(f"result:  {result}")
            return result

        except Exception as e:
                raise ValueError(f"❌ Błąd podczas analizy: {str(e)}")


    def ask_chat_about_details(self, text_from_ocr:str):
         
        prompt = f"""
            Użytkownik zrobił zdjęcie etykiety produktu spożywczego, następnie ze zdjęcia azure ImageAnalysisClient wyekstrachował tekst,
            który znajduje się na zdjęciu. 
            Przeanalizuj informacje zawarte na tej etykiecie. 
            Jeżeli jest to produkt spożyczy uzupełnij JSONa o informacje zawarte na etykiecie. W odpowiedzi zwróć JSON dokładnie w takim formacie: 
            Przykład:
            {GPTModel.json_schema}
            Do pola ingredients_that_may_appear wpisz te składniki, które na etykicie są jako Może zawierać.
            Twoim zadaniem jest wyciągnąć wartości odżywcze w formacie JSON. 
            Wyświetl **dwie sekcje**:  
                1. `per_100g` - wartości odżywcze w jednostce bazowej (np. 100g lub 100ml).  
                2. `per_serving`  wartości odżywcze dla jednej porcji, jeśli jest podana.  
            - Jeśli jakaś wartość nie jest dostępna, po prostu ją pomiń.  
            - Podawaj wartości dokładnie takie, jakie są na etykiecie, nie obliczaj ich sam.  
            - Wartości numeryczne jako liczby, jednostki dokładnie takie, jak w OCR.  
            - Nie mieszaj jednostki bazowej z porcją.  
            - Sprawdź czy na pewno nie pomyliłeś per_100g i per_serving   
            Jeżeli nie ma podanych wartości odżywczych pomiń, nie wymyślaj, nie szukaj
            W oby przypadkach uzupełnij w jsonie pole info - dodając w nim informację o porcji lub jednostce. Nazwy wartości odżywczych wpisz w polu name  w języku polskim
            Spróbuj wyciągnąć z teskty wartości kcal i dodać do jsona. Zwróć uwagę na to czy do dobrego pola w jsona wstawiasz wyniki dla porcji i dla danej jednostki
            Jeżeli po analizie tekstu uznasz że etykieta nie dotyczy produktu spożywczego, uzupełnij w jsonie pole product_name i product_type. W product_type wpisz NoFood
            Jeżeli na etykicie wykryjesz inny język niż polski, przetłumacz na polski.
            Wyszukaj informacji o plusach, minusach danego produktu. Kto powinien go unikać oraz ogólne rekomendacje. Dodaj te informacje w jsonie w sekcji     "consumer_notes"

            Tu jest tekst z OCRa {text_from_ocr}
        """
        try:
            response = self.client.chat.completions.create(
                model=AzureClientFactory.CHAT_DEPLOYMENT,
                messages=[
                    {
                        "role": "system",
                        "content": "Jesteś ekspertem który zna się na składach i wartościach odżywczych spodproduktów spożywczych. Ze szczególną uwagą podaj wartości odżywcze per_serving i per_100g"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3  # Niska temperatura = bardziej obiektywna analiza
            )

            #print(f"Wynik:  {response.choices[0].message.content.strip()}")
            result = response.choices[0].message.content.strip()

            cleaned = result.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[len("```json"):].strip()
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3].strip()

            return cleaned
        
        except Exception as e:
                raise ValueError(f"❌ Błąd podczas analizy: {str(e)}")

    json_schema =  {
    "product_name": "Pasztet drobiowy",
    "product_type": "Food",
    "ingredients": [
        {
            "name": "mięso oddzielone mechanicznie (MOM)",
            "category": "wysoko przetworzony",
            "controversial": True,
            "reason": "niska jakość mięsa"
        },
        {
            "name": "skóry z kurcząt",
            "category": "przetworzony",
            "controversial": True
        },
        {   "name": "musztarda", 
            "category": "przetworzony", 
            "subingredients": [
                 { "name": "woda",
                    "category": "naturalny"},
                    {
                    "name": "gorczyca",
                    "category": "naturalny",
                    "allergen": True,
                    "allergen_type": "gorczyca"
                    }],
        },
        {
            "name": "wątroba z kurcząt",
            "category": "naturalny"
        },
        {
            "name": "białko sojowe",
            "category": "wysoko przetworzony",
            "allergen": True,
            "allergen_type": "soja"
        },
        {
            "name": "maltodekstryna",
            "category": "wysoko przetworzony",
            "health_concern": "medium",
            "reason": "wysoki indeks glikemiczny"
        },
        {
            "name": "ekstrakt drożdżowy",
            "category": "wysoko przetworzony",
            "controversial": True,
            "reason": "wzmacniacz smaku"
        }],
    "ingredients_that_may_appear": [     {
            "name": "białko sojowe",
            "category": "wysoko przetworzony",
            "allergen": True,
            "allergen_type": "soja"
    }],
    "nutrition_per_portion":  {
        "info" : "w porcji (ok. 145g)" ,
        "energy": {"value": 873, "unit": "kJ", "name":"Wartość energetyczna"},
        "fat": {"value": 16, "unit": "g", "name":"Tłuszcz"},
        "saturated_fat": {"value": 5.5, "unit": "g", "name":"w tym kwasy tłuszczowe nasycone"},
        "salt": {"value": 0.14, "unit": "g", "name":"sól"},
    },
    "nutrition_in_unit": {
        "info" : "w 100g produktu" ,
        "energy": {"value": 873, "unit": "kJ", "name":"Wartość energetyczna"},
        "fat": {"value": 16, "unit": "g", "name":"Tłuszcz"},
        "saturated_fat": {"value": 5.5, "unit": "g", "name":"w tym kwasy tłuszczowe nasycone"},
        "salt": {"value": 0.14, "unit": "g", "name":"sól"},
    },
    "quality_score": 3,
    "consumer_notes": {
        "pros": ["wartościowe podroby", "warzywa i przyprawy"],
        "cons": ["MOM", "tanie wypełniacze", "cukry", "wzmacniacze smaku"],
        "who_should_avoid": ["alergicy", "osoby unikające przetworzonej żywności"],
        "recommendation": "Lepiej wybrać pasztet o prostym składzie: mięso + tłuszcz + warzywa + przyprawy. Unikać produktów z MOM oraz hydrolizatami białek."
    }
}     