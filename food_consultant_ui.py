import io
import base64
import json
import ast
import gradio as gr
from PIL import Image
from NutritionCoachApp import Analyzator

def process_image(image):
    if image is None:
        return "Brak zdjęcia", "Brak zdjęcia","Brak zdjęcia","Brak zdjęcia","Brak zdjęcia","Brak zdjęcia"
    
    analyzator = Analyzator()
    result = analyzator.try_analyze(image)   
    recipe = ""
    
    # result_dict = result.literal_eval(result)
    # print(f"result: {result} ")
    result_dict = json.loads(result)
    print(f"result_dict: {result_dict} ")
    if result_dict['product_name']:
        product_name = f'<div class="product-title"> {result_dict['product_name']} </div>'
        if result_dict['product_type'] == 'Food':
            recipe = analyzator.get_recipes_from_rag(result_dict['product_name'])
            print(f"recipe1: {recipe}")
        else:
            return "Na zdjęciu nie ma produktu spożywczego", "Na zdjęciu nie ma produktu spożywczego","Na zdjęciu nie ma produktu spożywczego"," ","Na zdjęciu nie ma produktu spożywczego","Na zdjęciu nie ma produktu spożywczego"    
    

    skladniki, allergens = get_ingredients(result_dict)
    print(f"skladniki: {skladniki} allergens: {allergens}")
    alergeny = allergens
    
    informacje = get_info(result_dict)
    print(f"informacje: {informacje}")
    wartosci_odzywcze = (
        (format_nutrition(result_dict["nutrition_in_unit"]) + "\n\n") if result_dict.get("nutrition_in_unit") else "") + (format_nutrition(result_dict["nutrition_per_portion"]) if result_dict.get("nutrition_per_portion") else "")
    return  wartosci_odzywcze, alergeny, informacje, product_name, skladniki, recipe

def get_info(result_dict):
    result_str = ""
    if result_dict.get('consumer_notes'):
        consumer_notes = result_dict.get('consumer_notes')
        if consumer_notes.get('pros'):
            result_str += "\n".join([f"➕ {item}" for item in consumer_notes.get('pros')])
            result_str += "\n"    
        if consumer_notes.get('cons'):
            result_str += "\n".join([f"➖ {item}" for item in consumer_notes.get('cons')])
            result_str += "\n"       
        if consumer_notes.get('who_should_avoid'):
            result_str += "\n".join([f"🚫 {item}" for item in consumer_notes.get('who_should_avoid')])
            result_str += "\n"  
        if consumer_notes.get('recommendation'):
            result_str += "\n💡 "+consumer_notes.get('recommendation')

    return result_str   

def format_nutrition(nutrition):
    lines = []
    if nutrition:
        info = nutrition.get("info")
        if info:
            lines.append(info)
        
        for key, value in nutrition.items():
            if key == "info":
                continue
            if isinstance(value, dict):
                name = value.get("name", key)
                val = value.get("value")
                unit = value.get("unit", "")
                if val is not None:
                    lines.append(f"   • {name}: {val} {unit}")
        
    return "\n".join(lines)

#print(format_nutrition(nutrition_in_unit))


def get_ingredients(ingredients):
    skladniki_array = []
    skladniki_str = ""
    allergens = []
    print(f"get_ingredients: {ingredients} ")
    if ingredients.get('ingredients'):
        for ingredient in ingredients.get('ingredients'):
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
                            sub_ingredient += subingredient['name'] 
                        if subingredient.get('reason'):
                            sub_ingredient += " - "
                            sub_ingredient += subingredient.get("reason", "")
                        if subingredient.get('allergen_type'):
                            allergens.append(f"• {subingredient['allergen_type']}") 
                        skladniki_str += sub_ingredient+'\n'

    ingredients_that_may_appear = []
    if ingredients.get('ingredients_that_may_appear'):
        for ingredient in ingredients.get('ingredients_that_may_appear'):
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
    # print(skladniki_str,'\n'.join(allergens_set) + '\n' + (may_appear))
    return skladniki_str,'\n'.join(allergens_set) + '\n' + (may_appear)



def _to_data_url(img: Image.Image, fmt: str = "JPEG") -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    mime = "image/jpeg" if fmt.upper() == "JPEG" else f"image/{fmt.lower()}"
    return f"data:{mime};base64,{b64}"



def create_ui():
    custom_css = """
    .main-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 10px;
    }
    .product-title {
        text-align: center;
        font-size: 1.5em;
        font-weight: bold;
        color: #2E7D32;
        margin-bottom: 20px;
        padding: 20px;
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 10px;
    }
    .info-box {
        font-family: monospace;
        font-size: 0.95em;
        line-height: 1.6;
    }
    """
    
    with gr.Blocks(css=custom_css, title="Konsultant spożywczy") as demo:

        gr.HTML('<div class="main-title">🍎 Konsultant spożywczy 🥗</div>')
        
        with gr.Row():
            with gr.Column(scale=1):
                image_input = gr.Image(
                    label="Zdjęcie etykiety produktu",
                    type="filepath",
                    height=400,
                    show_fullscreen_button=False,
                    show_label=False,
                    show_download_button=False,
                    show_share_button=False,
                    sources=["upload"]
                )
                
                analyze_btn = gr.Button(
                    "🔍 Analizuj etykietę",
                    variant="primary",
                    size="lg"
                )

            with gr.Column(scale=1):
                product_name = gr.HTML('<div class=class="hidden"> </div>')

                with gr.Tabs():
                    with gr.Tab("📝 Składniki"):
                        ingredients = gr.Textbox(
                            label="Składniki",
                            lines=20,
                            interactive=False,
                            elem_classes="info-box",
                            autoscroll=True
                        )
                    with gr.Tab("📊 Wartości odżywcze"):
                        nutrition_output = gr.Textbox(
                            label="Wartości odżywcze",
                            lines=20,
                            interactive=False,
                            elem_classes="info-box",
                            max_lines=50,
                        )
                    
                    with gr.Tab("⚠️ Alergeny"):
                        allergens_output = gr.Textbox(
                            label="Alergeny",
                            lines=20,
                            interactive=False,
                            elem_classes="info-box"
                        )
                    
                    with gr.Tab("ℹ️ Informacje"):
                        info_output = gr.Textbox(
                            label="Szczegółowe informacje",
                            lines=20,
                            interactive=False,
                            elem_classes="info-box"
                        )

                    with gr.Tab("ℹ️ Przepis"):
                        recipe = gr.Textbox(
                            label="Przepis",
                            lines=20,
                            interactive=False,
                            elem_classes="info-box"
                        )    
            
        gr.Markdown("---")
        
        gr.Markdown("""
        ---
        ### 💡 Jak używać:
        1. Zrób zdjęcie etykiety produktu lub prześlij istniejące zdjęcie
        2. Kliknij "Analizuj etykietę"
        3. Przejrzyj wyniki w zakładkach powyżej
        
        """)
        
        analyze_btn.click(
            fn=process_image,
            inputs=[image_input],
            outputs=[nutrition_output, allergens_output, info_output, product_name, ingredients, recipe]
        )
    
    return demo


def process_image_with_azure(image):
    """
    Funkcja z integracją Azure Computer Vision
    Podłącz tutaj swój kod OCR
    """
    if image is None:
        return "Brak zdjęcia", "", "", ""
    pass


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        share=False,        
        server_name="0.0.0.0",  
        server_port=7860,  
        show_error=True    
    )
    
