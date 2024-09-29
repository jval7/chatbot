from fastapi import routing

from app.bootstrap import BootStrap

rag_router = routing.APIRouter()

bs = BootStrap()


def handler(event: dict, context: dict) -> None:
    bs.get_chat_service().start_conversation()  # type: ignore
    return
