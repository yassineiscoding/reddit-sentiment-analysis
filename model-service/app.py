from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

app = FastAPI()


class SentimentRequest(BaseModel):
    text: str


# Load the tokenizer and model from local directory
try:
    tokenizer = DistilBertTokenizer.from_pretrained('./model')
    model = DistilBertForSequenceClassification.from_pretrained('./model',
                                                                state_dict=torch.load('./model/pytorch_model.bin',
                                                                                      map_location=torch.device('cpu')))
except Exception as e:
    print(f"Error loading model or tokenizer: {e}")
    raise

sentiment_labels = ['neutral', 'with palestine', 'with israel']

@app.post("/predict")
async def predict(request: SentimentRequest):
    try:
        inputs = tokenizer(request.text, return_tensors='pt', truncation=True, padding=True, max_length=512)
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.softmax(logits, dim=1)
        sentiment = torch.argmax(predictions, dim=1).item()
        sentiment_label = sentiment_labels[sentiment]
        return {"sentiment": sentiment_label}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
