import requests
from app.utils.auth import get_token
from app.services.project import get_organizations

with requests.Session() as session:
    token = get_token(session)
    journal = get_organizations(session, token, "655f142e5b102a26e732bfc4")
    print(journal)
