from repositories.database_repository import DatabaseRepository
from repositories.vector_repository import VectorRepository
from sentence_transformers import SentenceTransformer


class MetadataIngestion:

    def __init__(self):
        self.db = DatabaseRepository()
        self.vector = VectorRepository()

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    #########################################################
    # Metadata
    #########################################################

    async def generate_metadata(
        self,
        datasource: str
    ):
        return await self.db.fetch_metadata( datasource )

    #########################################################
    # Chunking
    #########################################################

    async def chunk(
        self,
        metadata: list
    ):

        chunks = []
        for table in metadata:

            text = f"""
            Table: {table['table']}
            Description: { table['description'] }
            Columns:
            {", ".join(table["columns"])}

            Relationships:
            {table.get("relationships", [])}
            """

            chunks.append(
                {
                    "table": table["table"],
                    "text": text
                }
            )

        return chunks

    #########################################################
    # Embeddings
    #########################################################

    async def embed(
        self,
        chunks: list
    ):

        for chunk in chunks:

            chunk["embedding"] = (
                self.embedding_model
                .encode(chunk["text"])
                .tolist()
            )

        return chunks

    #########################################################
    # Main Pipeline
    #########################################################

    async def index(
        self,
        datasource: str
    ):
        metadata = await self.generate_metadata( datasource )
        chunks = await self.chunk( metadata )
        chunks = await self.embed( chunks )

        await self.vector.insert( datasource, chunks )

        return {
            "status": "success",
            "tables": len(metadata),
            "chunks": len(chunks)
        }