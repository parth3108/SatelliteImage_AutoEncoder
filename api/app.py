from fastapi import FastAPI,Response,Request
from library import sateval
from models.base_response import BaseResponse
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
 
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

se = sateval.SatEval("dataset")
 
@app.get("/")
def status(response:Response,request:Request):
    return BaseResponse(True,200,"Success",data={"status": "API is running"}).respond(response=response)
 
 
@app.get("/get_config_template")
def get_config_template(response: Response, request: Request):
 
    try:
        result = se.configurables.get_config_template()
        return BaseResponse(True, 200, "Get Config Template Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Config Template Failed", data=str(ex)).respond(response=response)

    
@app.get("/get_pipeline_config_template")
def get_config_template(response: Response, request: Request):
 
    try:
        result = se.configurables.get_pipeline_config_template()
        return BaseResponse(True, 200, "Get Pipeline Config Template Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Pipeline Config Template Failed", data=str(ex)).respond(response=response)
    


@app.post("/validate_pipeline_config")
async def validate_pipeline_config(response: Response, request: Request):
 
    try:
        config = await request.json()
        result = se.configurables.validate_pipeline_config(config=config,clf=se)
        return BaseResponse(True, 200, "Pipeline Validation Complete", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Pipeline Validation Failed", data=str(ex)).respond(response=response)
 
@app.post("/validate_config")
async def validate_config(response: Response, request: Request):
    try:
        config = await request.json()
        result = se.configurables.validate_config(config=config, clf=se)
        return BaseResponse(True, 200, "Config Validation Complete", data=result).respond(response=response)
    except Exception as ex:
        return BaseResponse(False, 500, "Config Validation Failed", data=str(ex)).respond(response=response)
    

@app.get("/get_modules")
def get_modules(response: Response, request: Request):
    try:
        result = se.configurables.get_modules(se)
        return BaseResponse(True, 200, "Get Modules Success", data=result).respond(response=response)
    except Exception as ex:
        return BaseResponse(False, 500, "Get Modules Failed", data=str(ex)).respond(response=response)


@app.get("/get_methods/{module_name}")
def get_methods(module_name: str, response: Response, request: Request):
    try:
        result = se.configurables.get_methods(se, module_name)
        return BaseResponse(True, 200, f"Get Methods for {module_name} Success", data=result).respond(response=response)
    except Exception as ex:
        return BaseResponse(False, 500, f"Get Methods for {module_name} Failed", data=str(ex)).respond(response=response)
    
@app.get("/list_directories")
def list_directories(response: Response, request: Request):
    try:
        result = se.dataset_loader.list()
        return BaseResponse(True, 200, f"List Directories Success", data=result).respond(response=response)
    except Exception as ex:
        return BaseResponse(False, 500, f"List Directories Failed", data=str(ex)).respond(response=response)
    
@app.get("/get_evalauation_fields")
def get_evalauation_fields(response: Response, request: Request):
    try:
        result = se.evaluator.get_evalauation_fields()
        return BaseResponse(True, 200, f"Get Evaluation Fields Success", data=result).respond(response=response)
    except Exception as ex:
        return BaseResponse(False, 500, f"Get Evaluation Fields Failed", data=str(ex)).respond(response=response)



@app.post("/run_pipeline")
def run_pipeline(response: Response, request: Request, run_id: str):
 
    try:
        config = asyncio.run(request.json())
                
        return StreamingResponse(se.configurables.run(run_id,config=config,clf=se))
    except Exception as ex:
        return BaseResponse(False, 500, "Get Config Template Failed", data=str(ex)).respond(response=response)

@app.get("/get_run_ids")
def get_run_ids(response: Response, request: Request):
 
    try:
        result = se.evaluator.get_run_ids()
        return BaseResponse(True, 200, "Get Run IDs Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Run IDs Failed", data=str(ex)).respond(response=response)
    
@app.get("/get_evaluation_ids")
def get_evaluation_ids(response: Response, request: Request,run_id:str):
 
    try:
        result = se.evaluator.get_evaluation_ids(run_id=run_id)
        return BaseResponse(True, 200, "Get Evaluation IDs Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Evaluation IDs Failed", data=str(ex)).respond(response=response)
    

@app.get("/get_results_by_run_id")
def get_results_by_run_id(response: Response, request: Request,run_id:str):
 
    try:
        result = se.evaluator.get_results_by_run_id(run_id=run_id)
        return BaseResponse(True, 200, "Get Result by Run IDs Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Result by Run IDs Failed", data=str(ex)).respond(response=response)
    
@app.post("/get_image_by_path")
async def get_image_by_path(response: Response, request: Request):
 
    try:
        paths = await request.json()
        result = se.evaluator.get_image_by_path(paths[0])
        return BaseResponse(True, 200, "Get Image By Path Success", data=result).respond(response=response)
    except Exception as ex:    
        return BaseResponse(False, 500, "Get Image By Path Failed", data=str(ex)).respond(response=response)
