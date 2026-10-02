from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.conversation.orchestrator import ConversationOrchestrator
from app.models import GuidanceResponse, ClinicianSummary, Language
from app.persistence.models import SessionRow, MessageRow
from sqlalchemy import select

router = APIRouter(prefix="/v1", tags=["v1"])

class V1MessageRequest(BaseModel):
    session_id: Optional[str] = None
    text: str
    language: Language = Language.EN

@router.post("/conversation/message")
async def post_message(payload: V1MessageRequest, request: Request) -> GuidanceResponse:
    orchestrator: ConversationOrchestrator = request.app.state.orchestrator
    session_id = payload.session_id
    if not session_id:
        session = orchestrator.create_session(payload.language)
        session_id = session.id
        
    return await orchestrator.handle_message(session_id, payload.text)

@router.get("/clinical/summary/{session_id}")
def get_summary(session_id: str, request: Request) -> ClinicianSummary:
    orchestrator: ConversationOrchestrator = request.app.state.orchestrator
    history = orchestrator.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    for response in reversed(history.responses):
        if response.clinician_summary:
            return response.clinician_summary
            
    raise HTTPException(status_code=404, detail="Summary not found")

class SessionListItem(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    preview: str
    status: str

@router.get("/history/sessions")
def list_sessions(request: Request) -> List[SessionListItem]:
    orchestrator: ConversationOrchestrator = request.app.state.orchestrator
    session_factory = orchestrator._sessions._session_factory
    
    items = []
    with session_factory() as sa:
        sessions = sa.scalars(select(SessionRow).order_by(SessionRow.created_at.desc())).all()
        for s in sessions:
            first_msg = sa.scalars(select(MessageRow).where(MessageRow.session_id == s.id).order_by(MessageRow.seq)).first()
            last_msg = sa.scalars(select(MessageRow).where(MessageRow.session_id == s.id).order_by(MessageRow.seq.desc())).first()
            
            preview = first_msg.text if first_msg else "New Session"
            updated_at = datetime.fromisoformat(last_msg.created_at) if last_msg else datetime.fromisoformat(s.created_at)
            
            items.append(SessionListItem(
                id=s.id,
                created_at=datetime.fromisoformat(s.created_at),
                updated_at=updated_at,
                preview=preview,
                status=s.status
            ))
            
    return items
