import json
from pathlib import Path


class DatasetWriterAgent:

    async def save(self, datasource, retrieval_dataset, generation_dataset):
        retrieval_path = Path(f"offline/dataset_generator/datasets/retrieval/{datasource}_v1.json")
        generation_path = Path(f"offline/dataset_generator/datasets/generation/{datasource}_v1.json")
        retrieval_path.parent.mkdir( parents=True, exist_ok=True )
        generation_path.parent.mkdir( parents=True, exist_ok=True )
        retrieval_path.write_text( json.dumps( retrieval_dataset, indent=4 ))
        generation_path.write_text( json.dumps( generation_dataset, indent=4 ))