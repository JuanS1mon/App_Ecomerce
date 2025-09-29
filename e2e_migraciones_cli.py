import os
import time
import json
import requests
from typing import Callable

BASE_URL = os.getenv("TEST_BASE_URL", "http://127.0.0.1:8000")
USERNAME = os.getenv("TEST_USER", "juan")
# Credenciales por defecto alineadas con entorno de desarrollo (ver /auth/login-debug)
PASSWORD = os.getenv("TEST_PASS", "juan123")
ALT_PASSWORD = os.getenv("TEST_PASS_ALT", "123456")


def with_retries(fn: Callable[[], requests.Response], retries: int = 3, delay: float = 1.0):
    last_exc = None
    for i in range(retries):
        try:
            return fn()
        except Exception as ex:
            last_exc = ex
            time.sleep(delay)
    raise last_exc


def get_token():
    # Pide JSON para obtener el access_token directo
    try:
        r = with_retries(lambda: requests.post(
            f"{BASE_URL}/auth/login",
            headers={"Accept": "application/json"},
            data={"username": USERNAME, "password": PASSWORD},
            timeout=15,
        ))
        if r.status_code == 200:
            data = r.json()
            token = data.get("access_token")
            if not token:
                raise RuntimeError(f"No token in response: {data}")
            return token
        elif r.status_code == 401:
            # Intentar con password alternativo conocido del entorno de desarrollo
            r2 = with_retries(lambda: requests.post(
                f"{BASE_URL}/auth/login",
                headers={"Accept": "application/json"},
                data={"username": USERNAME, "password": ALT_PASSWORD},
                timeout=15,
            ))
            if r2.status_code == 200:
                data = r2.json()
                token = data.get("access_token")
                if not token:
                    raise RuntimeError(f"No token in response: {data}")
                return token
            # caemos al fallback si tampoco entra
        else:
            r.raise_for_status()
    except Exception as ex:
        print("Login directo falló, usando fallback de debug:", ex)

    # Fallback DEV: usar endpoint de debug para obtener token vía redirect Location
    dbg = with_retries(lambda: requests.get(
        f"{BASE_URL}/auth/login-debug/{USERNAME}",
        allow_redirects=False,
        timeout=10,
    ))
    loc = dbg.headers.get("Location", "")
    if "token=" in loc:
        # extraer token de la query
        from urllib.parse import urlparse, parse_qs

        qs = parse_qs(urlparse(loc).query)
        token_list = qs.get("token")
        if token_list:
            return token_list[0]
    # Intentar como último recurso el endpoint login-force
    force = with_retries(lambda: requests.get(
        f"{BASE_URL}/auth/login-force/{USERNAME}",
        timeout=10,
    ))
    if force.status_code == 200:
        data = force.json()
        if data.get("access_token"):
            return data["access_token"]
    raise RuntimeError(
        f"Fallback debug/force sin token. DebugStatus={dbg.status_code} Location='{loc}' ForceStatus={force.status_code}"
    )

def ensure_sample_csv():
    tmp = os.path.join(os.environ.get("TEMP", "."), "sample_migracion.csv")
    if not os.path.exists(tmp):
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("id,nombre,valor\n1,A,10\n2,B,20\n3,C,30\n4,D,40\n5,E,50\n")
    return tmp


def upload_file(token: str, path: str):
    files = {"file": (os.path.basename(path), open(path, "rb"), "text/csv")}
    data = {"migration_name": "prueba_agent"}
    try:
        r = requests.post(
            f"{BASE_URL}/migraciones/upload",
            headers={"Authorization": f"Bearer {token}"},
            files=files,
            data=data,
            timeout=60,
        )
        return r
    finally:
        files["file"][1].close()


def check_progress(token: str):
    r = with_retries(lambda: requests.get(
        f"{BASE_URL}/migraciones/check_progress",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        timeout=15,
    ))
    if r.status_code == 401:
        print("Auth error:", r.text)
    r.raise_for_status()
    return r.json()


def main():
    print("Login...")
    token = get_token()
    print("Token OK (trunc):", token[:20], "...")

    csv_path = ensure_sample_csv()
    print("Uploading:", csv_path)
    resp = upload_file(token, csv_path)
    print("Upload status:", resp.status_code)
    try:
        print("Upload body:", resp.json())
    except Exception:
        print("Upload body (text):", resp.text[:200])

    print("Polling progress...")
    start = time.time()
    for i in range(30):
        data = check_progress(token)
        stage = data.get("stage") or "n/a"
        pct = data.get("upload_percentage") if stage == "uploading" else data.get("progress_percentage")
        status = data.get("status")
        print(f"[{i:02d}] stage={stage} pct={pct} status={status}")
        if stage == "completed" or (status and "complet" in status.lower()) or (pct and pct >= 100):
            break
        time.sleep(2)
    print("Done in", round(time.time() - start, 1), "s")


if __name__ == "__main__":
    main()
