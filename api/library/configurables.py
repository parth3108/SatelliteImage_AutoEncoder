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
    
    def validate_pipeline_config(self,config:list,clf):
        if not isinstance(config,list):
            return False
        
        for item in config:
            if not isinstance(item,dict):
                return False
            if not "execution_path" in item:
                return False
            if not "params" in item:
                return False
        
        try:
            for item in config:
                if not self.validate_config(item,clf):
                    return False
        except Exception as ex:
            raise ex
                        
            
        return True
    
    def validate_config(self,config:dict,clf):
        if not isinstance(config,dict):
            return False
        
        keys = [
            "execution_path",
            "params"
        ]
        
        for key in keys:
            if not key in config:
                return False
        
        # validate using method and module and signature
        
        module = config["execution_path"].split(":")[0]
        method = config["execution_path"].split(":")[1]

        if not hasattr(clf,module):
            return False
        
        module = getattr(clf,module)

        if not hasattr(module,method):
            return False
        
        method = getattr(module,method)

        signature = inspect.signature(method)
        params = config["params"]

        for param in params:            
            if not param in signature.parameters:
                raise Exception("Parameter {} not found in method signature".format(param))
            if not isinstance(params[param],signature.parameters[param].annotation):
                raise Exception("Parameter {} is not of type {}".format(param,signature.parameters[param].annotation)) 

            
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
            
            modules[name] = type(obj).__name__

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
                    parameters[param] = str(signature.parameters[param].annotation).replace("<class '","").replace("'>","")
                methods[name] = {
                    "type":type(obj).__name__,
                    "parameters":parameters
                }
                
            
        return methods


    def run(self,run_id:str,config:dict,clf):

        try:
            for item in config:
                if not self.validate_config(item,clf):
                    return    
        except Exception as ex:
            yield "Exception: Pipeline config validation failed: {}".format(str(ex))

        try:
            yield "Pipeline with Run ID: {} Started".format(run_id)   
            for item in config:            
                for res in self.run_item(run_id,item,clf):
                    yield res
        except Exception as ex:
            yield "Exception: Error running pipeline: {}".format(str(ex))

        yield "Pipeline with Run ID: {} completed".format(run_id)
        return

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
        try:                     
            yield "Running module: {} method: {} with params: {}".format(module_name,method_name,params)
            for res in method(**params):
                yield res            
        except Exception as ex:
            yield str(ValueError("Error running method: {}".format(str(ex))))
