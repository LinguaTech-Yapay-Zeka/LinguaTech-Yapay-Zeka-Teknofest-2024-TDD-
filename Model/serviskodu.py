import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field

from model_fonksiyonlari import calistir

app = FastAPI()

class Item(BaseModel):
    text: str = Field(..., example="""Fiber 100mb SuperOnline kullanıcısıyım yaklaşık 2 haftadır @Twitch @Kick_Turkey gibi canlı yayın platformlarında 360p yayın izlerken donmalar yaşıyoruz.  Başka hiç bir operatörler bu sorunu yaşamazken ben parasını verip alamadığım hizmeti neden ödeyeyim ? @Turkcell """)

@app.post("/predict/", response_model=dict)
async def predict(item: Item):
    results = calistir(item.text)


    return results

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=8000)