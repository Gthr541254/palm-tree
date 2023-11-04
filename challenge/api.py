import fastapi
import pandas as pd
from pydantic import BaseModel, ValidationError
from typing import Annotated, Union, Literal, List

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from challenge.model import DelayModel

app = fastapi.FastAPI()
model = DelayModel()
model.pickle_load()

class Flight(BaseModel):
    OPERA: str
    TIPOVUELO: Literal['N', 'I']
    MES: Annotated[int, fastapi.Body(gt=0,lt=13)]
    
class Flights(BaseModel):
    flights: List[Flight]

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"error": "Parameter validation error"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Parameter validation error"})


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(flights: Flights) -> dict:
    df = pd.DataFrame(fastapi.encoders.jsonable_encoder(flights.flights))
    df = model.preprocess(df)
    return {
        "predict": model.predict(df)
    }
