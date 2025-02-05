import requests
from app.utils.auth import get_token
from app.services.project import get_filtered_projects
from app.services.user import get_current_user
from app.services.build_control.documents import get_project_documents

try:
    session = requests.Session()

    # Ваш действительный access token
    token = get_token(session)

    # Вызов функции с фильтрами
    projects = get_filtered_projects(session=session, access_token=token)

    print("Успешно получены проекты:")
    print(projects)

    user = get_current_user(session, token)
    if user:
        print(
            get_project_documents(
                session, token, "655f142e5b102a26e732bfc4", user["id"]
            )
        )

except Exception as e:
    print(f"Ошибка при получении проектов: {e}")
