from .dataset_loader import DatasetLoader
from .configurables import Configurables

class SatEval:
    dataset_loader:DatasetLoader
    configurables:Configurables    

    def __init__(self,dataset_dir:str):
        self.dataset_loader = DatasetLoader(dataset_dir)
        self.configurables = Configurables()

