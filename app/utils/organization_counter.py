import pandas as pd
import requests
from app.services.user import get_users_by_ids


def count_by_organizations(rows: pd.DataFrame, column_for_sort: str):
    """
    Возвращает словарь следующего вида:
    key:"organizations_count" - количество строк по организациям
    key:"general_count" - количество строк всего
    """
    general_count = len(rows)
    organizations_count = rows[column_for_sort].value_counts().reset_index()
    organizations_count = organizations_count.explode(column_for_sort)
    df_count = organizations_count.groupby(column_for_sort)["count"].sum().reset_index()
    df_count = df_count.rename(columns={column_for_sort: "author"})
    return {"organizations_count": df_count, "general_count": general_count}


def count_by_user_id(
    session: requests.Session, access_token: str, rows: pd.DataFrame, user_column: str
):
    general_count = len(rows)
    user_count = rows[user_column].value_counts().reset_index()
    user_ids = user_count[user_column].to_list()
    users = get_users_by_ids(
        session, access_token, user_ids if isinstance(user_ids, list) else []
    )
    organizations = users["attributes"].apply(lambda x: x["current_organisation_id"])
    raw_result = pd.concat([organizations, user_count["count"]], axis="columns")
    result = raw_result.groupby("attributes")["count"].sum().reset_index()
    result = result.rename(columns={"attributes": "author"})
    return {"organizations_count": result, "general_count": general_count}
