import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm
import pdfplumber
from configparser import ConfigParser
from dotenv import load_dotenv
from pymilvus import connections, Collection, utility
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import CrossEncoder
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from prompt import prompt_generator
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.vectorstores import Milvus


import logging
import warnings
# Suppress all warnings
warnings.filterwarnings("ignore")


flag = False

class ZiraatBankQA:
    def __init__(self, config_path, logger=None):
        self.config = self.load_config(config_path)
        self.creds, self.project_id = self.get_wml_creds()
        self.model_id = self.config['DEFAULT']['ModelID']
        self.embeddings = HuggingFaceInstructEmbeddings(model_name=self.config['DEFAULT']['EmbeddingsModel'])

        self.text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ' '],
            chunk_size=1000,
            chunk_overlap=150,
            length_function=len
        )
        self.collection_name = os.getenv("CollectionName", None)
        self.host = self.config['Milvus']['Host']
        self.port = self.config['Milvus']['Port']
        self.user = self.config['Milvus']['User']
        self.password = os.getenv('milvus_password', None)
        self.server_pem_path = self.config['Milvus']['ServerPemPath']
        self.server_name = self.config['Milvus']['ServerName']
        self.logger = logger if logger else logging.getLogger(__name__)

    def load_config(self, config_path):
        config = ConfigParser()
        config.read(config_path)
        return config

    def get_wml_creds(self):
        load_dotenv()
        api_key = os.getenv("API_KEY", None)
        ibm_cloud_url = os.getenv("IBM_CLOUD_URL", None)
        project_id = os.getenv("PROJECT_ID", None)
        if api_key is None or ibm_cloud_url is None or project_id is None:
            raise ValueError("Ensure you copied the .env file that you created earlier into the same directory as this script")
        creds = {
            "url": ibm_cloud_url,
            "apikey": api_key
        }
        return creds, project_id

    def send_to_watsonxai(self, prompt):
        params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 200,
            GenParams.TEMPERATURE: 0,
        }
        model = Model(model_id=self.model_id, params=params, credentials=self.creds, project_id=self.project_id)
        response = model.generate_text(prompt)
        return response

    def load_documents(self, folder_path):
        text_chunks = []
        files = glob.glob(os.path.join(folder_path, '*.pdf'))
        for file in tqdm(files):
            with pdfplumber.open(file) as pdf:
                data = ''.join([page.extract_text() for page in pdf.pages])
            created_text_chunks = self.text_splitter.create_documents([data])
            for chunk in created_text_chunks:
                chunk.metadata['file'] = file
                text_chunks.append(chunk)
        return text_chunks

    def create_vector_store(self, text_chunks):
        self.logger.info("Starting connection to Milvus.")
        connections.connect(
            "default",
            host=self.host,
            port=self.port,
            secure=True,
            server_pem_path=self.server_pem_path,
            server_name=self.server_name,
            user=self.user,
            password=self.password
        )

        self.logger.info("Checking if collection exists.")
        if utility.has_collection(self.collection_name):
            self.logger.info(f"***** Collection '{self.collection_name}' already exists. Using the existing collection.")
            vector_db = Milvus(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                connection_args={
                    "host": self.host,
                    "port": self.port,
                    "secure": True,
                    "server_pem_path": self.server_pem_path,
                    "server_name": self.server_name,
                    "user": self.user,
                    "password": self.password
                }
            )
        else:
            self.logger.info(f"Collection '{self.collection_name}' does not exist. Creating a new collection.")
            vector_db = Milvus.from_documents(
                text_chunks,
                self.embeddings,
                connection_args={
                    "host": self.host,
                    "port": self.port,
                    "secure": True,
                    "server_pem_path": self.server_pem_path,
                    "server_name": self.server_name,
                    "user": self.user,
                    "password": self.password
                },
                collection_name=self.collection_name
            )
            self.logger.info(f"Collection '{self.collection_name}' created successfully.")
            collection = Collection(self.collection_name)
            collection.load()
        
        self.logger.info("Vector store creation process complete.")
        return vector_db

    def perform_qa(self, df, query):
        context = "\n\n".join(df['paragraph'])
        prompt = prompt_generator(context, query)
        response = self.send_to_watsonxai(prompt)
        return response, context

    def main(self, query, folder_path=None):
        if folder_path:
            text_chunks = self.load_documents(folder_path)
            vector_db = self.create_vector_store(text_chunks)
        else:
            vector_db = Milvus(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                connection_args={
                    "host": self.host,
                    "port": self.port,
                    "secure": True,
                    "server_pem_path": self.server_pem_path,
                    "server_name": self.server_name,
                    "user": self.user,
                    "password": self.password
                }
            )

        if not vector_db:
            raise ValueError("Collection does not exist or could not be loaded.")
        
        docs = vector_db.similarity_search_with_score(query, k=15, ef=7)
        model = CrossEncoder('emrecan/bert-base-turkish-cased-mean-nli-stsb-tr', max_length=512)
        _docs = pd.DataFrame(
            [(query, doc[0].page_content, doc[0].metadata.get('file'), doc[1]) for doc in docs],
            columns=['query', 'paragraph', 'document', 'relevant_score']
        )
        scores = model.predict(_docs[['query', 'paragraph']].to_numpy())
        _docs['score'] = scores
        df = _docs[:15]
        response, context = self.perform_qa(df, query)
        self.logger.info(f"Response: {response}")
        return response, context
