import requests


def get_filtered_projects(
    session: requests.Session,  # Принимаем сессию с куками
    access_token: str,
    category: str | None = None,
    city: str | None = None,
    city_area: str | None = None,
    city_districts: str | None = None,
    status: str | None = None,
    base_url: str = "https://exv.portal.alabuga.ru",
    timeout: float = 10.0,
) -> dict:
    """
    Улучшенная версия с поддержкой сессии и кук

    :param session: Сессия requests с авторизационными куками
    :param ... остальные параметры без изменений
    """
    url = f"{base_url}/api/project-service/filtered-projects"

    payload = {
        "category": category,
        "city": city,
        "cityArea": city_area,
        "cityDistricts": city_districts,
        "status": status,
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": "https://exv.portal.alabuga.ru/projects",
        "Origin": "https://exv.portal.alabuga.ru",
        "Authorization": f"Bearer {access_token}",
    }

    try:
        response = session.post(url=url, json=payload, headers=headers, timeout=timeout)

        response.raise_for_status()
        return response.json()

    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response content: {response.text}")
        raise
    except Exception as e:
        print(f"General error: {e}")
        raise
