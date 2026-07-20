from repositories.database_repository import ( DatabaseRepository )
from repositories.vector_repository import ( VectorRepository )
from ingestion import ( MetadataIngestion )


class MCPServices:

    def __init__(self):
        self.db = ( DatabaseRepository())
        self.vector = ( VectorRepository() )
        self.ingestion = ( MetadataIngestion() )
    #########################################################
    # Retrieve Schema
    #########################################################

    async def retrieve_schema( self, question: str, datasource: str ) -> dict:

        metadata = await (self.vector.search( question=question, datasource=datasource ))
        relationships = await (self._expand_relationships( metadata, datasource ))
        return {
            "tables": metadata,
            "relationships": relationships
        }


    #########################################################
    # Execute SQL
    #########################################################

    async def execute_sql( self, sql: str, datasource: str ):
        return await ( self.db.execute_sql( sql, datasource ) )


    #########################################################
    # Refresh Metadata
    #########################################################

    async def refresh_metadata( self, datasource: str ):
        return await ( self.ingestion.index( datasource  ))

    #########################################################
    # Datasources
    #########################################################

    async def get_datasources( self ):
        return await ( self.db.get_datasources() )

    #########################################################
    # Relationships
    #########################################################

    async def _expand_relationships( self, metadata, datasource
    ):
        tables = []
        for item in metadata:
            tables.append(item["table"])
        return await ( self.db.fetch_relationships( datasource, tables ))
    
    async def get_schema_metadata(self, datasource):
        return await self.ingestion.generate_metadata(datasource)
    