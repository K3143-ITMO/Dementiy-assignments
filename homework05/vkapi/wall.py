import textwrap
import time
import typing as tp
from string import Template

import pandas as pd
from pandas import json_normalize
from requests.api import post

from vkapi import config, session
from vkapi.exceptions import APIError


def get_posts_2500(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
) -> tp.Dict[str, tp.Any]:

    if fields:
        code_fields = "?".join(fields)
    else:
        code_fields = ""

    code = f"""
    var result = [];
    var cursor = {offset};
    while (cursor < {max_count + offset}) {{
        var frame = API.wall.get({{
            "owner_id": "{owner_id}",
            "domain": "{domain}",
            "offset": cursor,
            "count": {count},
            "extended": {extended},
            "filter": "{filter}",
            "fields": "{code_fields}",
            "v": "{config.VK_CONFIG["version"]}"
        }});
        cursor = cursor + 100;
        result.push(frame);
    }}
    return result;
    """

    response = session.post(
        url="execute",
        data={
            "code": code,
            "access_token": config.VK_CONFIG["access_token"],
            "v": config.VK_CONFIG["version"],
        },
    ).json()
    if "response" in response:
        return response["response"]
    raise APIError


def get_wall_execute(
    owner_id: str = "",
    domain: str = "",
    offset: int = 0,
    count: int = 10,
    max_count: int = 2500,
    filter: str = "owner",
    extended: int = 0,
    fields: tp.Optional[tp.List[str]] = None,
    progress=None,
) -> pd.DataFrame:
    """
    Возвращает список записей со стены пользователя или сообщества.

    @see: https://vk.com/dev/wall.get

    :param owner_id: Идентификатор пользователя или сообщества, со стены которого необходимо получить записи.
    :param domain: Короткий адрес пользователя или сообщества.
    :param offset: Смещение, необходимое для выборки определенного подмножества записей.
    :param count: Количество записей, которое необходимо получить (0 - все записи).
    :param max_count: Максимальное число записей, которое может быть получено за один запрос.
    :param filter: Определяет, какие типы записей на стене необходимо получить.
    :param extended: 1 — в ответе будут возвращены дополнительные поля profiles и groups, содержащие информацию о пользователях и сообществах.
    :param fields: Список дополнительных полей для профилей и сообществ, которые необходимо вернуть.
    :param progress: Callback для отображения прогресса.
    """

    post_frame = get_posts_2500(
        owner_id, domain, offset, count, max_count, filter, extended, fields
    )["items"]
    print(post_frame)

    return json_normalize(post_frame)
