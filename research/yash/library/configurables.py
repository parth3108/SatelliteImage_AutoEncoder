class Configurables:

    def __init__(self):
        pass


    def get_config_template(self):
        return {
                "execution_path":"dataset_loader:load_by_url",
                "params":{
                    "key":"value"
                }

            }
    
    def get_pipeline_config_template(self):
        return [
            {
                "execution_path":"dataset_loader:load_by_url",
                "params":{
                    "key":"value"
                }

            }
        ]
    
    def validate_pipeline_config(self,config:list):
        if not isinstance(config,list):
            return False
        
        for item in config:
            if not isinstance(item,dict):
                return False
            if not "execution_path" in item:
                return False
            if not "params" in item:
                return False
            
        return True
    
    def validate_config(self,config:dict):
        if not isinstance(config,dict):
            return False
        
        keys = [
            "execution_path",
            "params"
        ]
        
        for key in keys:
            if not key in config:
                return False
            
        return True
    
    def get_execution_path(self,config:dict):
        return config["execution_path"]
    
    def get_params(self,config:dict):
        return config["params"]
    
    # dynamically load the module and class and run

    def run(self,config:dict,clf):

        for item in config:
            if not self.validate_config(item):
                return False     

        for item in config:
            self.run_item(item,clf)

    def run_item(self,config:dict,clf):
        execution_path = self.get_execution_path(config)
        params = self.get_params(config)
        executables = execution_path.split(":")
        module_name = executables[0]
        method_name = executables[1]

        # dynamically load the module from clf
        module = getattr(clf,module_name)
        method = getattr(module,method_name)

        # run the method
        method(**params)        
