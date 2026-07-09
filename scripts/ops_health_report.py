import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import urljoin


BASE_URL = "https://techeouro.net"
EXPECTED_ADSENSE = "ca-pub-2757348402596933"
EXPECTED_ADS_TXT = "pub-2757348402596933"
EXPECTED_GOOGLE_ADS = "AW-1827959532"
EXPECTED_ROUTES = [
    "/",
    "/mercados",
    "/ouro",
    "/economia",
    "/tech",
    "/desporto",
    "/paises",
    "/noticias",
    "/sobre",
    "/terminal",
    "/geopolitica",
    "/loja",
]


def fetch(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TechEOuro-OpsHealth/1.0"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read().decode("utf-8", errors="replace")
        return response.status, body


def check_route(route):
    url = urljoin(BASE_URL, route)
    status, body = fetch(url)
    title_match = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
    title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else ""
    return {
        "route": route,
        "status": status,
        "title": title,
        "page_not_found": "Page not found" in body,
    }


def check_local_files():
    required = [
        "index.html",
        "style.css",
        "script.js",
        "ads.txt",
        "_redirects",
        ".github/workflows/ai_news.yml",
        "scripts/update_news.py",
    ]
    missing = [path for path in required if not Path(path).exists()]
    return missing


def main():
    failures = []
    print("Tech & Ouro operational report")
    print(f"Base URL: {BASE_URL}")
    print("")

    missing = check_local_files()
    if missing:
        failures.append("Missing local files: " + ", ".join(missing))
    else:
        print("Local files: OK")

    print("")
    print("Routes:")
    for route in EXPECTED_ROUTES:
        try:
            result = check_route(route)
            marker = "OK" if result["status"] == 200 and not result["page_not_found"] else "FAIL"
            print(f"- {marker} {route}: {result['status']} {result['title']}")
            if marker != "OK":
                failures.append(f"Route {route} returned {result['status']} or Page not found")
        except Exception as exc:
            print(f"- FAIL {route}: {exc}")
            failures.append(f"Route {route} failed: {exc}")

    print("")
    try:
        _, home = fetch(BASE_URL + "/")
        checks = {
            "Google Ads tag": EXPECTED_GOOGLE_ADS in home,
            "AdSense script/account": EXPECTED_ADSENSE in home,
        }
        for name, ok in checks.items():
            print(f"{name}: {'OK' if ok else 'FAIL'}")
            if not ok:
                failures.append(name)
    except Exception as exc:
        failures.append(f"Home tag check failed: {exc}")

    try:
        _, ads_txt = fetch(BASE_URL + "/ads.txt")
        ok = EXPECTED_ADS_TXT in ads_txt
        print(f"ads.txt: {'OK' if ok else 'FAIL'}")
        if not ok:
            failures.append("ads.txt publisher id missing")
    except Exception as exc:
        failures.append(f"ads.txt failed: {exc}")

    print("")
    if failures:
        print("Status: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Status: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
