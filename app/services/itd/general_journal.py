import pandas
import requests

from app.services.build_control import documents
from app.utils.to_data_frame import dataframe


def _get_general_journal_all(
    session: requests.Session,
    access_token: str,
    project_id: str,
    is_actual: bool = True,
    **kwargs,
) -> dict | None:
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


def _get_materials_info(
    session: requests.Session, access_token: str, project_id: str
) -> dict | None:
    """
    Получает информацию о материалах проекта.

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :return: Объект ответа requests
    """
    url = f"https://exv.portal.alabuga.ru/api/itd-service/general-journal/project/{project_id}/materials-info"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": f"Bearer {access_token}",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    response = session.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["materials"]
    return None


def _get_documents_info(
    session: requests.Session, access_token: str, project_id: str
) -> dict | None:
    """
    Получает информацию о документах проекта.

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :return: Объект ответа requests
    """
    url = f"https://exv.portal.alabuga.ru/api/itd-service/general-journal/project/{project_id}/documents-info"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": f"Bearer {access_token}",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Access-Control-Allow-Methods": "GET, PUT, POST, DELETE",
        "Access-Control-Allow-Origin": "*",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    response = session.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()["itdDocuments"]
    return None


def _get_unit_measures(
    session: requests.Session, access_token: str, project_id: str
) -> dict | None:
    """
    Получает информацию о единицах измерения для проекта.

    :param session: Сессия requests
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :return: Объект ответа requests
    """
    url = f"https://exv.portal.alabuga.ru/api/catalog-service/unit-measures/projects/{project_id}"

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
    }

    response = session.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Ответ в формате JSON, нужный для обработки
    return None


def _get_work_types(
    session: requests.Session, access_token: str, project_id: str
) -> dict | None:
    """
    Получает информацию о типах работ проекта.

    :param session: Сессия requests (куки передаются автоматически)
    :param access_token: Токен авторизации
    :param project_id: ID проекта
    :return: JSON-ответ API или None, если запрос не удался
    """
    url = f"https://exv.portal.alabuga.ru/api/catalog-service/work-types/projects/{project_id}"

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
        "Referer": f"https://exv.portal.alabuga.ru/projects/{project_id}/itd/general-journal-three",
    }

    response = session.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    return None


@dataframe
def ger_general_journal(
    session: requests.Session, access_token: str, project_id: str
) -> pandas.DataFrame:
    general_journal = _get_general_journal_all(session, access_token, project_id)
    materials = _get_materials_info(session, access_token, project_id)
    unit = _get_unit_measures(session, access_token, project_id)
    document = _get_documents_info(session, access_token, project_id)
    work_types = _get_work_types(session, access_token, project_id)
