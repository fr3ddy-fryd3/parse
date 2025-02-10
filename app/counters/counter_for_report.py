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


def _add_sum_row(df: pd.DataFrame, count: int):
    df_count = pd.DataFrame({"author": ["Итого"], "count": count})
    return pd.concat([df, df_count], axis="rows")


def _prepare_count_table(df: pd.DataFrame, index: list[str], column_name: str):
    df = (
        df.set_index("author")
        .reindex(index)
        .fillna(0)
        .rename_axis("Организация")
        .rename(columns={"count": column_name})
    )
    df[column_name] = df[column_name].astype(int)
    return df


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
    organizations_list = list(organizations_table.values())
    organizations_list.append("Итого")

    table_header = [
        "Реестр ИД",
        "Раздел 3 ОЖР",
        "Исп. схемы",
        "Перечень работ",
        "Материалы",
        "Замечания",
        "Инспекции",
    ]

    ### поулчение итоговой таблицы по ИТД

    itds["author"] = itds["author"].apply(lambda x: _find_organization_name(x))
    result = count_by_organizations(itds, "author")
    itds_count = result["general_count"]
    itds_count_by_organizations = result["organizations_count"]
    itds_count_by_organizations = _add_sum_row(itds_count_by_organizations, itds_count)

    ### получение итоговой таблицы по ОЖР

    result = count_by_organizations(journal, "organisationId")
    journal_count = result["general_count"]
    journal_count_by_organizations = result["organizations_count"]
    journal_count_by_organizations = _translate_id_to_name(
        journal_count_by_organizations, organizations_table
    )
    journal_count_by_organizations = _add_sum_row(
        journal_count_by_organizations, journal_count
    )

    ### получение итоговой таблицы по исполнительным схемам

    executive_schemas["author"] = executive_schemas["author"].apply(
        lambda x: _find_organization_name(x)
    )
    result = count_by_organizations(executive_schemas, "author")
    executive_schemas_count = result["general_count"]
    executive_schemas_count_by_organizations = result["organizations_count"]
    executive_schemas_count_by_organizations = _add_sum_row(
        executive_schemas_count_by_organizations, executive_schemas_count
    )

    ### получение итоговой таблицы по перечню работ

    result = count_by_user_id(session, access_token, project_tasks, "userId")
    project_tasks_count_by_organizations = result["organizations_count"]
    project_tasks_count_by_organizations = _translate_id_to_name(
        project_tasks_count_by_organizations, organizations_table
    )
    project_tasks_count = result["general_count"]
    project_tasks_count_by_organizations = result["organizations_count"]
    project_tasks_count_by_organizations = _add_sum_row(
        project_tasks_count_by_organizations, project_tasks_count
    )

    ### получение итоговой таблицы по материалам

    result = count_by_organizations(materials, "permittedOrgIds")
    materials_count = result["general_count"]
    materials_count_by_organizations = result["organizations_count"]
    materials_count_by_organizations = _translate_id_to_name(
        materials_count_by_organizations, organizations_table
    )
    materials_count_by_organizations = _add_sum_row(
        materials_count_by_organizations, materials_count
    )

    ### получение итоговой таблицы по инспекциям

    project_inspections["author"] = project_inspections["authorUser"].apply(
        lambda x: x["organizationName"]
    )
    result = count_by_organizations(project_inspections, "author")
    project_inspections_count = result["general_count"]
    project_inspections_count_by_organizations = result["organizations_count"]
    project_inspections_count_by_organizations = _add_sum_row(
        project_inspections_count_by_organizations, project_inspections_count
    )

    ### получение итоговой таблицы по замечаниям

    project_remarks["author"] = project_remarks["authorUser"].apply(
        lambda x: x["organizationName"]
    )
    result = count_by_organizations(project_remarks, "author")
    project_remarks_count = result["general_count"]
    projects_remarks_count_by_organizations = result["organizations_count"]
    projects_remarks_count_by_organizations = _add_sum_row(
        projects_remarks_count_by_organizations, project_remarks_count
    )

    tables = [
        itds_count_by_organizations,
        journal_count_by_organizations,
        executive_schemas_count_by_organizations,
        project_tasks_count_by_organizations,
        materials_count_by_organizations,
        projects_remarks_count_by_organizations,
        project_inspections_count_by_organizations,
    ]

    for df, column_name in zip(tables, table_header):
        df = _prepare_count_table(df, organizations_list, column_name)

    tables = [
        _prepare_count_table(df, organizations_list, column_name)
        for df, column_name in zip(tables, table_header)
    ]

    result = pd.concat(tables, axis="columns")

    result["Итого"] = result.sum(axis=1)
    return result
