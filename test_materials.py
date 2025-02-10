from datetime import datetime
import requests
from app.services.itd import get_itd_sets
from app.utils.auth import get_token
from app.counters import get_documentation_report_breakdown_by_subcontractors
from app.counters.counter_for_report import _get_organizations_table

with requests.Session() as session:
    access_token = get_token(session)
    documents_count_by_organizations = (
        get_documentation_report_breakdown_by_subcontractors(
            session, access_token, "655f142e5b102a26e732bfc4"
        )
    )
    documents_count_by_organizations.to_excel(
        f"documentation_report_breakdown_by_subcontractors-{datetime.now()}.xlsx"
    )
