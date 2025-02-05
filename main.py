import requests
import pandas
from app.utils.auth import get_token
from app.services.project import get_filtered_projects
from app.services.itd.general_journal import get_general_journal_info

with requests.Session() as session:
    token = get_token(session)
    project = get_filtered_projects(session=session, access_token=token)
    data = get_general_journal_info(session, token, project.loc[0]["id"])
    data = data.sort_values("userId")
    data.to_excel("result.xlsx")
