import json
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import yagmail

# Load environment variables from .env file
load_dotenv()

HTML_PATH = "A동_회의실_예약현황_2023-10-03.html"
PREV_STATUS_PATH = "rooms_status_prev.json"

# Email configuration from environment variables
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")

# Validate that required email configuration is present
if not all([EMAIL_TO, EMAIL_FROM, EMAIL_APP_PASSWORD]):
    raise ValueError(
        "Missing email configuration. Please check your .env file.\n"
        "Required variables: EMAIL_TO, EMAIL_FROM, EMAIL_APP_PASSWORD\n"
        "Copy .env.example to .env and fill in your credentials."
    )

# 회의실 상태 스크래핑 함수(층 td와 회의실 td 인덱싱 구분해 전체 파싱)
def scrape_room_status():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"file://{Path(HTML_PATH).resolve()}")
        rows = page.query_selector_all("table tr")[2:]  # 0,1: 헤더
        status = {}
        for row in rows:
            tds = row.query_selector_all("td")
            if not tds:
                continue
            # 층 td가 붙은 첫 줄과 나머지 줄의 td 수 구분해서 파싱
            if tds[0].inner_text().endswith("층"):
                room = tds[1].inner_text()
                slot_start = 2
            else:
                room = tds[0].inner_text()
                slot_start = 1
            slots = [td.inner_text() for td in tds[slot_start:]]
            status[room] = slots
        browser.close()
    return status

def load_prev_status():
    if not Path(PREV_STATUS_PATH).exists():
        return None
    with open(PREV_STATUS_PATH, "r") as f:
        return json.load(f)

def save_status(status):
    with open(PREV_STATUS_PATH, "w") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)

def compare_status(prev, curr):
    if prev is None:
        return {}
    changed = {}
    for room, slots in curr.items():
        if room not in prev:
            changed[room] = {"new": slots}
        else:
            changes = [
                (i, prev[room][i], slots[i])
                for i in range(len(slots))
                if slots[i] != prev[room][i]
            ]
            if changes:
                changed[room] = changes
    return changed

def send_email(changes):
    yag = yagmail.SMTP(user=EMAIL_FROM, password=EMAIL_APP_PASSWORD)
    subject = "[Agent] 회의실 예약 상태 변경 알림"
    lines = []
    for room, changes_list in changes.items():
        if isinstance(changes_list, dict) and "new" in changes_list:
            lines.append(f"신규 회의실 {room} 추가/변경된 전체 슬롯!")
        else:
            for i, old, new in changes_list:
                # 시간 구하기 (08:00 기준)
                hour = 8 + (i // 2)
                minute = "00" if i % 2 == 0 else "30"
                tstr = f"{hour:02}:{minute}"
                lines.append(f"{room}: {tstr} {old} → {new}")
    body = "\n".join(lines)
    yag.send(EMAIL_TO, subject, body)
