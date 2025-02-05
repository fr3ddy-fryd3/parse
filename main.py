import requests
from app.utils.auth import get_token
from app.services.project import get_filtered_projects
from app.services.itd.materials import get_project_materials

try:
    session = requests.Session()

    # Ваш действительный access token
    token = get_token(session)

    # Вызов функции с фильтрами
    projects = get_filtered_projects(session=session, access_token=token)

    print("Успешно получены проекты:")
    print(projects)

    print(get_project_materials(session, token, "655f142e5b102a26e732bfc4"))

except Exception as e:
    print(f"Ошибка при получении проектов: {e}")
