from abc import ABC, abstractmethod
from rdflib import Graph, Literal, XSD, URIRef
from rdflib.plugins.sparql import prepareQuery
import datetime

class KnowledgeStorage(ABC):
    @abstractmethod
    def get(self, query: str, bindings = {}) -> list:
        pass

class N3KnowledgeStorage(KnowledgeStorage):
    def __init__(self, file_path: str):
        g = Graph()
        g.parse(file=open(file_path, "r"), format="n3")
        self.graph = g

    def get(self, query: str, bindings: dict = {}) -> list:
        q = prepareQuery(query)
        initBindings = self._prepare_bindings(bindings)

        result = self.graph.query(q, initBindings=initBindings)

        return list(result)

    def _prepare_bindings(self, bindings):
        result = {}

        for key, value in bindings.items():
            if isinstance(value, URIRef):
                result[key] = value
            elif isinstance(value, float):
                result[key] = Literal(value, datatype=XSD.float)
            elif isinstance(value, int):
                result[key] = Literal(value, datatype=XSD.integer)
            elif isinstance(value, str):
                result[key] = Literal(value, datatype=XSD.string)
            elif isinstance(value, bool):
                result[key] = Literal(value, datatype=XSD.boolean)
            elif isinstance(value, datetime.datetime):
                result[key] = Literal(value.isoformat(), datatype=XSD.dateTime)
            else:
                raise TypeError(f"Unsupported binding type for key '{key}': {type(value)}")

        return result
