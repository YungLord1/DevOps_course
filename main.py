from fastapi import FastAPI
from app.presentation import router
from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

# Основное приложение fastapi + подключаем эндпоинты
app = FastAPI(title="Currency Parser API")
app.include_router(router)

# main, подтягиваем порт из переменной окружения
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', '8000'))
    uvicorn.run(app, host="0.0.0.0", port=port)
    