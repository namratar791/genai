from typing import TypedDict


class DatasetState(TypedDict):

    datasource: str
    count: int
    metadata: dict
    questions: list
    retrieval_dataset: list
    generation_dataset: list