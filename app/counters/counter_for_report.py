from numpy import short
import pandas as pd
import requests
from app.utils import count_by_organizations, count_by_user_id
from app.services.build_control import (
    get_project_inspections,
    get_project_remarks,
)
from app.services.itd import (
    get_project_materials,
    get_executive_scheme_info,
    get_itd_sets,
    get_project_tasks,
    _get_general_journal_all,
)
from app.services.project import get_organizations


def _find_organization_name(name: str) -> str:
    index = name.find(" из ")
    name = name[index + 4 :]
    return name


def _translate_id_to_name(df: pd.DataFrame, translate_table: dict):
    df["author"] = df["author"].apply(lambda x: translate_table[x])
    return df


def _get_organizations_table(
    session: requests.Session, access_token: str, project_id: str
):
    organizations = get_organizations(session, access_token, project_id)
    organizations["organization"] = organizations["organization"].apply(
        lambda x: x["shortName"]
    )
    return organizations.set_index("organizationId")["organization"].to_dict()


def get_documentation_report_breakdown_by_subcontractors(
    session: requests.Session, access_token: str, project_id: str
):
    ### получение всей нужной информации для отчета

    itds = get_itd_sets(session, access_token, project_id)
    journal = _get_general_journal_all(session, access_token, project_id)
    executive_schemas = get_executive_scheme_info(session, access_token, project_id)
    project_tasks = get_project_tasks(session, access_token, project_id)
    materials = get_project_materials(session, access_token, project_id)
    project_inspections = get_project_inspections(session, access_token, project_id)
    project_remarks = get_project_remarks(session, access_token, project_id)

    organizations_table = _get_organizations_table(session, access_token, project_id)

    ### поулчение итоговой таблицы по ИТД

    itds["author"] = itds["author"].apply(lambda x: _find_organization_name(x))
    result = count_by_organizations(itds, "author")
    itds_count = result["general_count"]
    itds_count_by_organizations = result["organizations_count"]
    print(itds_count_by_organizations, "itds")

    ### получение итоговой таблицы по ОЖР

    result = count_by_organizations(journal, "organisationId")
    journal_count = result["general_count"]
    journal_count_by_organizations = result["organizations_count"]
    journal_count_by_organizations = _translate_id_to_name(
        journal_count_by_organizations, organizations_table
    )
    print(journal_count_by_organizations, "journal")

    ### получение итоговой таблицы по исполнительным схемам

    executive_schemas["author"] = executive_schemas["author"].apply(
        lambda x: _find_organization_name(x)
    )
    result = count_by_organizations(executive_schemas, "author")
    executive_schemas_count = result["general_count"]
    executive_schemas_count_by_organizations = result["organizations_count"]
    print(executive_schemas_count_by_organizations, "executive_schemas")

    ### получение итоговой таблицы по перечню работ

    result = count_by_user_id(session, access_token, project_tasks, "userId")
    project_tasks_count = result["general_count"]
    project_tasks_count_by_organizations = result["organizations_count"]
    project_tasks_count_by_organizations = _translate_id_to_name(
        project_tasks_count_by_organizations, organizations_table
    )
    print(project_tasks_count_by_organizations, "project_tasks")

    ### получение итоговой таблицы по материалам

    result = count_by_organizations(materials, "permittedOrgIds")
    materials_count = result["general_count"]
    materials_count_by_organizations = result["organizations_count"]
    materials_count_by_organizations = _translate_id_to_name(
        materials_count_by_organizations, organizations_table
    )
    print(materials_count_by_organizations, "materials")

    ### получение итоговой таблицы по инспекциям

    project_inspections["author"] = project_inspections["authorUser"].apply(
        lambda x: x["organizationName"]
    )
    result = count_by_organizations(project_inspections, "author")
    project_inspections_count = result["general_count"]
    project_inspections_count_by_organizations = result["organizations_count"]
    print(project_inspections_count_by_organizations, "project_inspections")

    ### получение итоговой таблицы по замечаниям

    project_remarks["author"] = project_remarks["authorUser"].apply(
        lambda x: x["organizationName"]
    )
    result = count_by_organizations(project_remarks, "author")
    project_remarks_count = result["general_count"]
    projects_remarks_count_by_organizations = result["organizations_count"]
    print(projects_remarks_count_by_organizations, "project_remarks")
    print(_get_organizations_table(session, access_token, project_id))
