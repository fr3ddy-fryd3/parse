import requests


def get_current_user(
    session: requests.Session,
    access_token: str,
) -> dict | None:
    """
    Получает данные текущего пользователя.

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :return: JSON-ответ или None при ошибке
    """
    url = "https://exv.portal.alabuga.ru/api/users-service/users/current"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Access-Control-Allow-Methods": "GET, PUT, POST, DELETE",
        "Access-Control-Allow-Origin": "*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Authorization": f"Bearer {access_token}",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Referer": "https://exv.portal.alabuga.ru/",
    }

    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None
