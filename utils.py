from qdrant_client import QdrantClient
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Qdrant

class QdrantVectorstore():
    def __init__(self, domain, store_api, store_host):
        self.embeddings = OpenAIEmbeddings()
        self.client = QdrantClient(host=store_host, api_key=store_api)
        self.vectorstore = Qdrant(
            self.client,
            domain,
            self.embeddings.embed_query,
            content_payload_key='text',
            metadata_payload_key='metadata'
        )