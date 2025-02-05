import requests


def get_executive_scheme_info(
    session: requests.Session,
    access_token: str,
    project_id: str,
    **kwargs,
) -> dict | None:
    """
    Получает минимальную информацию по исполнительной схеме проекта

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :param kwargs: Дополнительные параметры запроса
    :return: Объект ответа requests
    """
    base_url = (
        "https://exv.portal.alabuga.ru/api/itd-service/executive-scheme/allMinimal"
    )

    # Базовые заголовки
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
        "Priority": "u=0",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    # Параметры запроса
    params = {"projectId": project_id}
    params.update(kwargs)  # Добавляем дополнительные параметры

    # Выполняем запрос
    response = session.get(
        url=base_url,
        headers=headers,
        params=params,
    )

    if response.status_code == 200:
        return response.json()
    return None
