from offline.dataset_generator.workflows.dataset_workflow import (
    build_dataset_workflow
)


class DatasetGenerationAgent:

    def __init__(self):
        self.workflow = (build_dataset_workflow())

    async def run( self, datasource, metadata, count=30):
        return await ( self.workflow.ainvoke({"datasource": datasource, "count": count, "metadata": metadata }))