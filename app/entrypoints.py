from typing import Optional
import pydantic
from fastapi import Depends, UploadFile, HTTPException, APIRouter
from app.bootstrap import BootStrap
from app.logs import logger
from app.services.usecases import ChatService, NoChatFound, InputNotProvided

rag_router = APIRouter()
bs = BootStrap()

@rag_router.post("/chats/")
async def start_chat(service: ChatService = Depends(bs.get_chat_service)) -> dict:
    chat_id = service.start_conversation()
    return {"chat_id": chat_id}

class ContinueChatInput(pydantic.BaseModel):
    query: str

@rag_router.post("/chats/{conversation_id}/continue")
async def continue_chat(
    conversation_id: str,
    request_param: ContinueChatInput | None = None,
    service: ChatService = Depends(bs.get_chat_service),
) -> dict:
    logger.info(f"request_param: {request_param}")
    query = request_param.query if request_param else None
    try:
        response = service.continue_conversation(conversation_id, query, None)
        return {"response": response}
    except NoChatFound:
        raise HTTPException(status_code=404, detail="Chat not found")
    except InputNotProvided:
        raise HTTPException(status_code=400, detail="No input provided")

@rag_router.post("/chats/{conversation_id}/continue-with-voice")
async def continue_chat_with_voice(
    conversation_id: str,
    voice_file: Optional[UploadFile] = None,
    service: ChatService = Depends(bs.get_chat_service),
) -> dict:
    voice_file_bytes = await voice_file.read() if voice_file else None
    try:
        response = service.continue_conversation(conversation_id, None, voice_file_bytes)
        return {"response": response}
    except NoChatFound:
        raise HTTPException(status_code=404, detail="Chat not found")
    except InputNotProvided:
        raise HTTPException(status_code=400, detail="No input provided")
