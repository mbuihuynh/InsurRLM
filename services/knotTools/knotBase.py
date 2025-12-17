from utils.CBase import CBase
from utils.LoggingUtils import MessageTemplate

from dataclasses import dataclass
import os


class KNOTBase(CBase):
    """
        KNOTBase develop a modular RAG
    """

    def __init__(self,knot:dataclass, reasoning=True):
        super().__init__()

        self.knot = knot
        self.reasoning = reasoning

    def _init_(self):
        self.model = None

    def tool(self):
        output = None

        return output


if __name__ == "__main__":
    print("Hello KNOTBase Agent Template")

    
