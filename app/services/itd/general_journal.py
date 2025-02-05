import pandas
import requests
from app.utils.to_data_frame import dataframe


@dataframe
def get_general_journal_info(
    session: requests.Session,
    access_token: str,
    project_id: str,
    is_actual: bool = True,
    **kwargs,
) -> pandas.DataFrame | None:
    """
    Получает общую информацию по журналу проекта

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :param is_actual: Флаг актуальности данных (по умолчанию True)
    :param kwargs: Дополнительные параметры запроса
    :return: Объект ответа requests
    """
    base_url = f"https://exv.portal.alabuga.ru/api/itd-service/general-journal/project/{project_id}/allInfo"

    # Базовые заголовки
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": f"Bearer {access_token}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=0",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    # Параметры запроса
    params = {"isActual": str(is_actual).lower()}
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
