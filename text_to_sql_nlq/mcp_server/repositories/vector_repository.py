import os

from pinecone import Pinecone
from sentence_transformers import SentenceTransformer


class VectorRepository:

    def __init__(self):
        pc = Pinecone(
            api_key=os.getenv("PINECONE_API_KEY")
        )

        self.embedding_model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )

        self.index = pc.Index(
            os.getenv("PINECONE_INDEX")
        )

    async def insert(
        self,
        datasource: str,
        chunks: list
    ):

        vectors = []
        for chunk in chunks:
            vectors.append(
                {
                    "id": chunk["table"],
                    "values": chunk["embedding"],
                    "metadata": {
                        "table": chunk["table"],
                        "text": chunk["text"]
                    }
                }
            )

        self.index.upsert(
            vectors=vectors,
            namespace=datasource
        )

    async def search( self, question: str, datasource: str, top_k: int = 5 ):
        embedding = (
            self.embedding_model
            .encode(question)
            .tolist()
        )
        results = self.index.query( 
            vector=embedding,
            namespace=datasource,
            top_k=top_k,
            include_metadata=True
        )

        response = []
        for match in results.matches:
            response.append(
                {
                    "table": match.metadata["table"],
                    "score": match.score,
                    "text": match.metadata["text"]
                }
            )

        return response

    async def delete(
        self,
        datasource: str
    ):
        self.index.delete(
            delete_all=True,
            namespace=datasource
        )