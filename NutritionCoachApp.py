from image import ImageAnalyzer
from search import GPTModel
import ast
import json

class Analyzator:

    def try_analyze(self, image_path:str):
        #image_path = "photos\\other\\20251114_101336.jpg" #mydlo
        # image_path = "photos\\other\\mydlo-marsylskie-125g-imbir-i-kurkuma.jpg" #mydlo
        #image_path = "photos\\spozywka\\20251114_100705.jpg" #pomidory
        #image_path = "photos\\spozywka\\20251114_101104.jpg" #pomidory
        
        analyzer = ImageAnalyzer()
        gpt = GPTModel()

        result = analyzer.analyze(image_path)
        print(f"Wynik ze zdjęcia: {result.caption.text}")
        if result.read:
            for block in result.read.blocks:
                for line in block.lines:
                    print(f"- {line.text}")
        jsonFromImage = gpt.ask_chat(result.caption.text)
        result_dict = json.loads(jsonFromImage)
        # print(f"result_dict: {result_dict} ")
        if result_dict.get('product_name'):
            result_jsonFromImage = (
                jsonFromImage
                .replace("True", "true")
                .replace("False", "false")
                .replace("None", "null")
            )
            return result_jsonFromImage
        else:
            if self.is_text_on_photo(result) is True:
                self.validate_text_from_ocr(result)
                jsonResult = gpt.ask_chat_about_details(self.get_text_from_ocr(result))
                # print(f"{jsonResult}")
            
                result_json_from_ocr = (
                    jsonResult
                    .replace("True", "true")
                    .replace("False", "false")
                    .replace("None", "null")
                )
            return result_json_from_ocr

    def validate_text_from_ocr(self, result):
        all_lines = []
        low_confidence_items = []    
        sum_confidence = 0
        sum_words = 0
        sum_words_whit_low_confidence = 0
        min_confidence = 0.7

        for block in result.read.blocks:
            for line in block.lines:
                all_lines.append(line.text)
                    
                if hasattr(line, 'words'):
                    for word in line.words:
                        sum_words=sum_words+1
                        sum_confidence=sum_confidence+word.confidence

                        # print(f"{word.text} - {word.confidence} - {sum_words}")
                                
                        if word.confidence < min_confidence:
                            low_confidence_items.append(word.text)
                            sum_words_whit_low_confidence= sum_words_whit_low_confidence+1
            
        total_confidence = (sum_confidence/sum_words)*100
        if total_confidence < 70:
            raise ValueError("Total confidence is lower then 70. Try with another photo")

    def is_text_on_photo(self, result):
        if result.read:   
            return True
        else:
            return False

    def get_text_from_ocr(self, result):
        resultText = []
        for block in result.read.blocks:
            for line in block.lines:
                resultText.append(line.text)
        return '\n'.join(resultText)

    def get_recipes_from_rag(self, product_name):
        print("================== JESTEM W RAG")
        gpt = GPTModel()
        recipes =  gpt.get_recipes_from_rag(product_name)  
        print (f"recipes: {recipes}")
        return recipes

if __name__ == "__main__":
    try:
        analyzator = Analyzator()
        result = analyzator.try_analyze("photos\\spozywka\\20251114_101042.jpg")
        result_dict = ast.literal_eval(result)
        skladniki_array = []
        skladniki_str = ""
        allergens = []
        for ingredient in result_dict['ingredients']:
                one_ingredient = ""
                if ingredient['category'] == 'naturalny':
                    one_ingredient = "🟩 "
                elif ingredient['category'] == 'przetworzony':
                    one_ingredient ="🟧 "
                elif ingredient['category'] == 'wysoko przetworzony':
                    one_ingredient ="🟥 "      
                one_ingredient += ingredient['name'] 
                if ingredient.get('reason'):
                    one_ingredient += " - "
                one_ingredient += ingredient.get("reason", "")
                if ingredient.get('allergen_type'):
                    allergens.append(f"• {ingredient['allergen_type']}") 
                skladniki_str += one_ingredient+'\n'
                if ingredient.get('subingredients'):
                    for subingredient in ingredient.get('subingredients'):
                        sub_ingredient = ""
                        if subingredient.get('category'):
                            if subingredient['category'] == 'naturalny':
                                sub_ingredient = "     🟩 "
                            elif subingredient['category'] == 'przetworzony':
                                sub_ingredient = "     🟧 "
                            elif subingredient['category'] == 'wysoko przetworzony':
                                sub_ingredient = "     🟥 "      
                            sub_ingredient += sub_ingredient['name'] 
                        if subingredient.get('reason'):
                            sub_ingredient += " - "
                            sub_ingredient += subingredient.get("reason", "")
                        if subingredient.get('allergen_type'):
                            allergens.append(f"• {subingredient['allergen_type']}") 
                        skladniki_str += sub_ingredient+'\n'

        ingredients_that_may_appear = []
        for ingredient in result_dict['ingredients_that_may_appear']:
                if ingredient.get('allergen_type'):
                    ingredients_that_may_appear.append(f"• {ingredient['allergen_type']}") 

        ingredients_that_may_appear_set = set(ingredients_that_may_appear)
        may_appear = (
        "Składniki, które mogą wystąpić: \n" 
        + '\n'.join(ingredients_that_may_appear_set)
        if ingredients_that_may_appear_set else ""
        )

        #print(may_appear)

        allergens_set = set(allergens)
        print(skladniki_str,'\n'.join(allergens_set) + '\n' + (may_appear))

    except Exception as e:
        print(f"\n✗ Error: {e}")

