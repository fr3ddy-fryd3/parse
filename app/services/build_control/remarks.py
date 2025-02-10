import requests
import pandas as pd
from app.utils import dataframe


@dataframe
def get_project_remarks(
    session: requests.Session,
    access_token: str,
    project_id: str,
) -> pd.DataFrame:
    """
    Получает замечания проекта.

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :return: JSON-ответ или None при ошибке
    """
    url = f"https://exv.portal.alabuga.ru/api/sk-service/v2/remarks?projectId={project_id}"

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
        "Referer": f"https://exv.portal.alabuga.ru/projects/{project_id}/buildControl/remarks",
    }

    response = session.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None
