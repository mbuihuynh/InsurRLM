"""
    https://doc.agentscope.io/tutorial/task_rag.html
"""

from utils.CBase import CBase
from utils.LoggingUtils import MessageTemplate

from dataclasses import dataclass
import os

from agentscope.rag import SimpleKnowledge, QdrantStore, TextReader
from agentscope.embedding import DashScopeTextEmbedding

from configs.cf_knotbase import KnotBase



class KNOTBase(CBase):
    """
        KNOTBase develop a modular RAG
    """

    def __init__(self,knot:dataclass=KnotBase(), reasoning=True):
        super().__init__()

        self.knot = knot
        self.reasoning = reasoning

    def _init_(self):
        self.model = None

        self.knotBase = SimpleKnowledge(
            embedding_store=QdrantStore(
                location=self.knot.LOCATION,
                collection_name=self.knot.COLL_NAME,
                dimensions=self.knot.EMB_DIM
            ),
            embedding_model=DashScopeTextEmbedding(

            )
        )


    def tool(self):
        output = None

        return output


if __name__ == "__main__":
    print("Hello KNOTBase Agent Template")


