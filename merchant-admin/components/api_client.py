import os
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def _headers(user_id=None, skip_auth=False):
    headers = {"Content-Type": "application/json"}

    if skip_auth:
        return headers

    access_token = st.session_state.get("access_token")

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    return headers


def _handle_response(response):
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        try:
            error_detail = response.json()
        except Exception:
            error_detail = response.text

        raise Exception(f"{response.status_code} error: {error_detail}") from e

    return response.json() if response.text else {}


def api_get(path, user_id=None, skip_auth=False):
    response = requests.get(
        f"{API_BASE_URL}{path}",
        headers=_headers(user_id=user_id, skip_auth=skip_auth),
        timeout=30,
    )
    return _handle_response(response)


def api_post(path, payload=None, user_id=None, skip_auth=False):
    response = requests.post(
        f"{API_BASE_URL}{path}",
        json=payload or {},
        headers=_headers(user_id=user_id, skip_auth=skip_auth),
        timeout=30,
    )
    return _handle_response(response)


def api_put(path, payload=None, user_id=None, skip_auth=False):
    response = requests.put(
        f"{API_BASE_URL}{path}",
        json=payload or {},
        headers=_headers(user_id=user_id, skip_auth=skip_auth),
        timeout=30,
    )
    return _handle_response(response)


def api_delete(path, user_id=None, skip_auth=False):
    response = requests.delete(
        f"{API_BASE_URL}{path}",
        headers=_headers(user_id=user_id, skip_auth=skip_auth),
        timeout=30,
    )
    return _handle_response(response)
