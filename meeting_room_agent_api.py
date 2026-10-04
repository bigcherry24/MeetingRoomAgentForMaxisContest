from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List, Any
import json
from pathlib import Path
from agent_core import scrape_room_status, compare_status, load_prev_status, save_status, send_email

app = FastAPI(title="회의실 예약상태 감지 API Agent")

# 기본 엔드포인트
@app.get("/status", response_model=Dict[str, List[str]])
def get_status():
    """현재 예약 현황 리턴 + 최초면 status 저장"""
    status = scrape_room_status()
    if not Path("rooms_status_prev.json").exists():
        save_status(status)
    return status

@app.get("/changes", response_model=Dict[str, Any])
def get_changes():
    """마지막 비교 결과 리턴 (직전 상태와 현재 상태 차이)"""
    prev = load_prev_status()
    curr = scrape_room_status()
    changes = compare_status(prev, curr)
    return changes

class TriggerCheckResponse(BaseModel):
    has_changed: bool
    changes: Dict[str, Any]
    mail_sent: bool

@app.post("/trigger-check", response_model=TriggerCheckResponse)
def trigger_check():
    """강제 상태 변화 감지 및 이전 현황 업데이트, 변경시 email 알림"""
    prev = load_prev_status()
    curr = scrape_room_status()
    changes = compare_status(prev, curr)
    mail_sent = False
    save_status(curr)  # 변화 여부와 관계 없이 항상 최신 상태 저장
    if changes:
        send_email(changes)
        mail_sent = True
    return {"has_changed": bool(changes), "changes": changes, "mail_sent": mail_sent}
