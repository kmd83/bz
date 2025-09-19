import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

GOALS = {
    "loss": "Схуднення",
    "maintain": "Підтримка",
    "gain": "Набір ваги",
}

ACTIVITY = {
    1: 1.2,   # Дуже низька
    2: 1.375, # Легка
    3: 1.55,  # Середня
    4: 1.725, # Висока
    5: 1.9,   # Дуже висока
}
