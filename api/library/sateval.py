from .dataset_loader import DatasetLoader
from .configurables import Configurables
from .preprocessor import PreProcessor
from .compressor import Compressor
from .decompressor import Decompressor
from .evaluator import Evaluator
from .simulated_noise_injector import SimulatedNoiseInjector

import sqlite3


class SatEval:
    dataset_loader:DatasetLoader
    configurables:Configurables    
    pre_processor:PreProcessor
    compressor:Compressor
    simulated_noise_injector:SimulatedNoiseInjector
    decompressor:Decompressor
    evaluator:Evaluator


    __connection:sqlite3.Connection

    def __init__(self,dataset_dir:str):
        self.__connection = sqlite3.connect('sateval.db',check_same_thread=False,autocommit=True)
        self.dataset_loader = DatasetLoader(f"data/{dataset_dir}",self.__connection)
        self.configurables = Configurables()
        self.pre_processor = PreProcessor()
        self.compressor = Compressor(self.__connection)
        self.simulated_noise_injector = SimulatedNoiseInjector(self.__connection)
        self.decompressor = Decompressor(self.__connection)
        self.evaluator = Evaluator(self.__connection)
        self.__migrate__()

    def __migrate__(self):
        with self.__connection:   
            self.__connection.execute(
                "CREATE TABLE IF NOT EXISTS datasets (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, path TEXT)"
            )
            self.__connection.execute(
                    "CREATE TABLE IF NOT EXISTS extracted_datasets (id INTEGER PRIMARY KEY AUTOINCREMENT, zip_file_path TEXT, destination_folder TEXT)"
            )
            self.__connection.execute(
                    "CREATE TABLE IF NOT EXISTS image_data (id INTEGER PRIMARY KEY AUTOINCREMENT,run_id TEXT,height INT,width INT,input_image_path TEXT, compressed_image_path TEXT, noisy_image_path TEXT,decompressed_image_path TEXT, input_image_size INTEGER, compressed_image_size INTEGER, noisy_image_size INTEGER, decompressed_image_size INTEGER,compression_time REAL, decompression_time REAL,results TEXT)"
            )
            self.__connection.commit()

