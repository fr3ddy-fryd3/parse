import base64
import hashlib
import json
import os
import re
import secrets
import time
from urllib.parse import parse_qs, urlparse

import json5
import requests

from config import Config


def _generate_code_verifier():
    """Генерация code_verifier для PKCE по RFC 7636"""
    token = secrets.token_urlsafe(96)
    return token[:128]  # Ограничение длины для некоторых реализаций OAuth


def _generate_code_challenge(verifier):
    """Генерация code_challenge методом S256"""
    digest = hashlib.sha256(verifier.encode("utf-8")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=")
    return challenge.decode("utf-8")


def _save_tokens(filepath: str, token_data: dict) -> None:
    """Сохраняет токены в файл с расчетом времени истечения"""
    token_data = token_data.copy()
    # Добавляем абсолютное время истечения
    token_data["expiration_time"] = time.time() + token_data["expires_in"]
    # Удаляем временные параметры которые не нужны для будущих сессий
    token_data.pop("expires_in", None)

    with open(filepath, "w") as f:
        json.dump(token_data, f, indent=2)


def _load_tokens(filepath: str) -> dict | None:
    """Загружает токены из файла и проверяет срок их действия"""
    if not os.path.exists(filepath):
        return None

    try:
        with open(filepath, "r") as f:
            token_data = json.load(f)

        # Проверяем наличие обязательных полей
        if not all(
            key in token_data
            for key in ["access_token", "refresh_token", "expiration_time"]
        ):
            raise ValueError("Invalid token file structure")

        # Проверяем срок действия
        if token_data["expiration_time"] < time.time():
            os.remove(filepath)  # Удаляем просроченный файл
            return None

        return token_data
    except (json.JSONDecodeError, KeyError, ValueError):
        os.remove(filepath)  # Удаляем битый файл
        return None


# Генерируем PKCE параметры
def get_token(session: requests.Session) -> str:
    if Config.TOKEN_FILE and (tokens := _load_tokens(Config.TOKEN_FILE)):
        print("Используем сохраненные токены")
        return tokens["access_token"]
    code_verifier = _generate_code_verifier()
    code_challenge = _generate_code_challenge(code_verifier)

    # Первый шаг: получение loginAction URL
    url = "https://exv.portal.alabuga.ru/auth/realms/SpringBoot/protocol/openid-connect/auth"
    params = {
        "client_id": "ExonReactApp",
        "redirect_uri": "https://exv.portal.alabuga.ru/callback",
        "response_type": "code",
        "scope": "email roles profile offline_access",
        "state": "random_state",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    response = session.get(url, params=params)
    html_content = response.text

    # Извлечение JavaScript-объекта из window.kcContext
    script_match = re.search(
        r"window\.kcContext\s*=\s*\(\(\)\s*=>\s*{([\s\S]*?)}\s*\)\s*\(\)\s*;",
        html_content,
    )
    if not script_match:
        raise ValueError("Не удалось найти объект kcContext")
    script_code = script_match.group(1)

    # Поиск объекта 'const out = {...};' внутри функции
    out_match = re.search(r"const out\s*=\s*({[\s\S]*?})\s*;", script_code)
    if not out_match:
        raise ValueError("Не удалось найти объект 'out'")
    json_str = out_match.group(1)

    # Очистка JSON строки
    json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)
    json_str = re.sub(r",\s*(?=}|\])", "", json_str)

    # Парсинг с помощью json5
    try:
        kc_context = json5.loads(json_str)
    except json5.JSONDecodeError as e:
        raise ValueError(f"Ошибка парсинга JSON: {e}")

    # Извлечение loginAction
    login_action = kc_context.get("url", {}).get("loginAction", "")

    # Разбиваем URL на компоненты
    parsed_url = urlparse(login_action)
    query_params = parse_qs(parsed_url.query)

    # Получаем значения параметров
    session_code = query_params.get("session_code", [""])[0]
    execution = query_params.get("execution", [""])[0]
    client_id = query_params.get("client_id", [""])[0]
    tab_id = query_params.get("tab_id", [""])[0]

    # Второй шаг: отправка POST-запроса для авторизации
    auth_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = {
        "session_code": session_code,
        "execution": execution,
        "client_id": client_id,
        "tab_id": tab_id,
    }

    body = {
        "username": Config.USERNAME,
        "password": Config.PASSWORD,
    }

    response = session.post(
        auth_url, headers=headers, params=params, data=body, allow_redirects=False
    )

    if response.status_code == 302:
        location = response.headers.get("location")
        if not location:
            raise ValueError("Заголовок Location не найден.")
    else:
        print(f"Ошибка авторизации. Код: {response.status_code}")
        print("Ответ:", response.text)
        exit()

    # Извлекаем code из URL
    parsed_url = urlparse(location)
    query_params = parse_qs(parsed_url.query)
    code = query_params.get("code", [""])[0]
    session_state = query_params.get("session_state", [""])[0]

    if not code:
        raise ValueError("Code не найден в URL.")

    # Получение токена
    token_url = "https://exv.portal.alabuga.ru/auth/realms/SpringBoot/protocol/openid-connect/token"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
        "Accept": "application/json",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    body = {
        "grant_type": "authorization_code",
        "redirect_uri": "https://exv.portal.alabuga.ru/callback",
        "code": code,
        "code_verifier": code_verifier,
        "client_id": "ExonReactApp",
    }

    response = session.post(token_url, headers=headers, data=body)
    response_data = response.json()

    if response.status_code == 200:
        print("\nУспешная аутентификация!")
    else:
        print(f"\nОшибка получения токена. Код: {response.status_code}")
        print("Ответ:", response.text)

    token_data = {
        "access_token": response_data["access_token"],
        "refresh_token": response_data["refresh_token"],
        "expires_in": response_data["expires_in"],
    }

    if Config.TOKEN_FILE:
        _save_tokens(Config.TOKEN_FILE, token_data)

    return token_data["access_token"]
