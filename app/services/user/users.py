import requests


def get_users_by_ids(session: requests.Session, token: str, user_ids: list):
    url = "https://exv.portal.alabuga.ru/api/users-service/users/get-users"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {token}",
    }

    response = session.post(url, headers=headers, json=user_ids)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return None
