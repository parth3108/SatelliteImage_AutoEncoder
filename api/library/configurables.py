import copy
import inspect


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
        params = copy.deepcopy(config["params"])
        if not isinstance(params, dict):
            params = {}  # or handle this case as needed
        return params
    

    def get_modules(self,clf):
        """
        Returns the modules of the clf with its type
        """
        modules = {}
        for name, obj in inspect.getmembers(clf):            
            if "__" in name:
                continue    

            if "configurables" in name:
                continue
            
            modules[name] = type(obj)
        return modules
    
    def get_methods(self,clf,module_name):
        """
        Returns the methods of the module with its type
        """
        module = getattr(clf,module_name)
        methods = {}
        for name, obj in inspect.getmembers(module):
            if '__' in name:
                continue

            if type(obj).__name__ == "method":
                # get parameters of the method with its data type
                signature = inspect.signature(obj)
                parameters = {}
                for param in signature.parameters:
                    if "run_id" in param:
                        continue
                    parameters[param] = signature.parameters[param].annotation
                methods[name] = {
                    "type":type(obj),
                    "parameters":parameters
                }
                
            
        return methods

    
    # dynamically load the module and class and run

    def run(self,run_id:str,config:dict,clf):

        for item in config:
            if not self.validate_config(item):
                return False     

        for item in config:
            self.run_item(run_id,item,clf)

    def run_item(self,run_id:str,config:dict,clf):
        execution_path = self.get_execution_path(config)
        params = self.get_params(config)        
        executables = execution_path.split(":")
        module_name = executables[0]
        method_name = executables[1]

        # dynamically load the module from clf
        module = getattr(clf,module_name)
        method = getattr(module,method_name)

        # check if the method accepts run_id
        signature = inspect.signature(method)

        for method_params in signature.parameters:            
            if "run_id" in method_params:
                params["run_id"] = run_id
                break
            
        # run the method
        method(**params)        
