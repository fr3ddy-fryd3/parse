import pandas as pd
import requests
from app.utils import dataframe


@dataframe
def get_organizations(
    session: requests.Session,
    access_token: str,
    project_id: str,
) -> pd.DataFrame:
    url = f"https://exv.portal.alabuga.ru/api/project-service/organizations/members/{project_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {access_token}",
    }

    response = session.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка {response.status_code}: {response.text}")
        return pd.DataFrame()
