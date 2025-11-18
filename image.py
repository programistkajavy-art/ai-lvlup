##
"""
    Pobranie danych ze zdjęcia
"""

from azure.ai.vision.imageanalysis.models   import VisualFeatures 
from azure.core.exceptions import HttpResponseError
from azure_client_factory import AzureClientFactory

class ImageAnalyzer:

    client = None

    def __init__(self):
        self.client = AzureClientFactory.get_image_analysis_client()

    def analyze(self, image_path: str):
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
                
            result = self.client.analyze(
                image_data=image_data,
                visual_features=[
                        VisualFeatures.CAPTION,       # Opis obrazu
                        VisualFeatures.READ,          # OCR - odczyt tekstu
                    ],
                language="en", gender_neutral_caption=False
            )

            # print("=== OPIS OBRAZU ===")
            # if result.caption:
            #     print(f"Opis: {result.caption.text}")
            #     print(f"Pewność: {result.caption.confidence:.2%}")
                
            # print("\n=== TEKST NA OBRAZIE (OCR) ===")
            # if result.read:
            #     for block in result.read.blocks:
            #         for line in block.lines:
            #             print(f"- {line.text}")

            return result            
                
        except FileNotFoundError:
                print(f"Plik {image_path} nie został znaleziony")
        except HttpResponseError as e:
                print(f"Błąd analizy: {e}")