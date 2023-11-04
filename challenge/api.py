import fastapi
from pydantic import BaseModel, ValidationError
from typing import Annotated, Union, Literal, List

from challenge.model import DelayModel

app = fastapi.FastAPI()
model = DelayModel()
model.pickle_load()

class Predict(BaseModel):
    OPERA: str
    TIPOVUELO: Literal['N', 'I']
    MES: Annotated[int, fastapi.Body(gt=0,lt=13)]

@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    return JSONResponse(status_code=400, content={"error": "Parameter validation error"})

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(flights: List[Predict]) -> dict:
    df = pd.DataFrame.from_dict(flights, orient='columns')
    df = model.preprocess(df)
    return {
        "predict": model.predict(df)
    }