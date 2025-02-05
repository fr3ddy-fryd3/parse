import requests
from app.auth import get_token
from app.services.project_service import get_filtered_projects

try:
    session = requests.Session()

    # Ваш действительный access token
    token = get_token(session)

    # Вызов функции с фильтрами
    projects = get_filtered_projects(
        session=session, access_token=token["access_token"]
    )

    print("Успешно получены проекты:")
    print(projects)

except Exception as e:
    print(f"Ошибка при получении проектов: {e}")
