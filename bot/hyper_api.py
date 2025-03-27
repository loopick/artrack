import requests
from config import API_URL, HEADERS

class HyperAPI:
    def get_positions(self, address):
        """Возвращает множество активных позиций пользователя по адресу."""
        try:
            response = requests.post(
                API_URL,
                json={"type": "clearinghouseState", "user": address},
                headers=HEADERS
            )
            data = response.json()
            return {pos["position"]["coin"] for pos in data.get("assetPositions", [])}
        except Exception as e:
            print(f"Ошибка запроса API для {address}: {e}")
            return None
