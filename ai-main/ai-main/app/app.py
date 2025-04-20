from fastapi import FastAPI, APIRouter, status, UploadFile, File
from ai import churn_prediction
from fastapi.responses import StreamingResponse
import io
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

router = APIRouter()

@router.post("/")
async def predict(file: UploadFile = File(...)):
    contents = await file.read()
    text_data = contents.decode("utf-8")
    
    file = io.StringIO(text_data)

    result_df = churn_prediction(file)
    
    stream = io.StringIO()
    result_df.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=predictions.csv"
    return response

app.include_router(router)