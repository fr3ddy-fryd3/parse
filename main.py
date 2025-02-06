from numpy import datetime_as_string
import requests
from datetime import datetime
from app.utils.auth import get_token
from app.services.itd import (
    _get_general_journal_all,
    _get_materials_info,
    _get_documents_info,
    _get_unit_measures,
    _get_work_types,
)

with requests.Session() as session:
    token = get_token(session)
    response = _get_work_types(session, token, "655f142e5b102a26e732bfc4")
    print(response)
