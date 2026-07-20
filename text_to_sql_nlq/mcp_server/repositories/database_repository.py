import os
from sqlalchemy import (create_engine, text, inspect )


class DatabaseRepository:

    def __init__(self):
        self.connections = {}

    def get_connection( self, datasource: str):
        if datasource not in self.connections:
            url = "sqlite:///./db/nlq_app.db"
            self.connections[datasource] = ( create_engine(url) )
        return self.connections[datasource]

    async def execute_sql( self, sql: str, datasource: str ):
        engine = self.get_connection( datasource )

        with engine.connect() as conn:
            result = conn.execute( text(sql) )
            rows = [
                dict(row._mapping)
                for row in result
            ]

        return rows

    async def fetch_metadata(self,datasource: str):
        engine = self.get_connection( datasource )
        inspector = inspect(engine)
        metadata = []
        with engine.connect() as conn:
            for table in inspector.get_table_names():
                columns = [
                    col["name"]
                    for col in inspector.get_columns(
                        table
                    )
                ]

                relationships = (
                    inspector.get_foreign_keys(
                        table
                    )
                )

                description_result = conn.execute( text(""" SELECT description FROM table_descriptions WHERE table_name = :table """ ), { "table": table }).fetchone()
                if description_result:
                    description = ( description_result .description )
                metadata.append(
                    {
                        "table": table,
                        "columns": columns,
                        "description": description,
                        "relationships": relationships
                    }
                )

        return metadata

    async def fetch_relationships(
        self,
        datasource: str,
        tables: list
    ):

        metadata = await self.fetch_metadata(
            datasource
        )

        relationships = []

        for item in metadata:

            if item["table"] in tables:

                relationships.extend(
                    item["relationships"]
                )

        return relationships