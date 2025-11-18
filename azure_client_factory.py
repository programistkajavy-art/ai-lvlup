import os
from dotenv import load_dotenv
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.core.credentials import AzureKeyCredential   
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)

class AzureClientFactory:
    load_dotenv()
    VISION_ENDPOINT = os.getenv('VISION_ENDPOINT2')
    VISION_KEY = os.getenv('VISION_KEY2')

    CHAT_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    CHAT_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    CHAT_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

    INDEX = "recipes"

    @staticmethod
    def get_image_analysis_client():
        if AzureClientFactory.validate_image_analysis_client() is True:
            try:
                client = ImageAnalysisClient(AzureClientFactory.VISION_ENDPOINT, AzureKeyCredential(AzureClientFactory.VISION_KEY))
                return client
            except Exception as e:
                print(f"Error during connection: {e}")
        

    @staticmethod
    def validate_image_analysis_client():
        if not AzureClientFactory.VISION_ENDPOINT:
            raise ValueError("Environment variable 'VISION_ENDPOINT2' is not set or empty.")
        if not AzureClientFactory.VISION_KEY:
            raise ValueError("Environment variable 'VISION_KEY' is not set or empty.")
        else:
            return True
        
    @staticmethod
    def validate_open_ai_client():
        if not AzureClientFactory.CHAT_API_KEY:
            raise ValueError("Environment variable 'CHAT_API_KEY' is not set or empty.")
        if not AzureClientFactory.CHAT_ENDPOINT:
            raise ValueError("Environment variable 'CHAT_ENDPOINT' is not set or empty.")
        if not AzureClientFactory.CHAT_DEPLOYMENT:
            raise ValueError("Environment variable 'CHAT_DEPLOYMENT' is not set or empty.")
        if not AzureClientFactory.CHAT_API_VERSION:
            raise ValueError("Environment variable 'CHAT_API_VERSION' is not set or empty.")
        else:
            return True    

    @staticmethod
    def get_azure_open_ai():
        if AzureClientFactory.validate_open_ai_client() is True:
            try:
                return AzureOpenAI(api_key=AzureClientFactory.CHAT_API_KEY, 
                                   api_version=AzureClientFactory.CHAT_API_VERSION, 
                                   azure_endpoint=AzureClientFactory.CHAT_ENDPOINT)
            except Exception as e:
                print(f"Error during connection: {e}")

    @staticmethod
    def get_search_index_client():
        if AzureClientFactory.validate_search_client() is True:
            try:
                client = SearchIndexClient(AzureClientFactory.AZURE_SEARCH_ENDPOINT, AzureKeyCredential(AzureClientFactory.AZURE_SEARCH_KEY))
                return client
            except Exception as e:
                print(f"Error during connection: {e}")

    @staticmethod
    def get_search_client():
        if AzureClientFactory.validate_search_client() is True:
            try:
                client = SearchClient(endpoint= AzureClientFactory.AZURE_SEARCH_ENDPOINT, credential= AzureKeyCredential(AzureClientFactory.AZURE_SEARCH_KEY), index_name=AzureClientFactory.INDEX)
                return client
            except Exception as e:
                print(f"Error during connection: {e}")            

    @staticmethod
    def validate_search_client():
        if not AzureClientFactory.AZURE_SEARCH_ENDPOINT:
            raise ValueError("Environment variable 'AZURE_SEARCH_ENDPOINT' is not set or empty.")
        if not AzureClientFactory.AZURE_SEARCH_KEY:
            raise ValueError("Environment variable 'AZURE_SEARCH_KEY' is not set or empty.")
        else:
            return True                