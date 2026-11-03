from typing import Literal, Optional

from pydantic import BaseModel


class Citation(BaseModel):
    document_id: str
    page: int
    element_id: str


class ProposedAction(BaseModel):
    type: Literal["create_ticket"]
    equipment_id: str
    title: str
    description: str


class MaintiDocAnswer(BaseModel):
    status: Literal["answered", "needs_clarification", "abstained"]
    answer: str
    citations: list[Citation] = []
    uncertainties: list[str] = []
    clarification_question: Optional[str] = None
    proposed_action: Optional[ProposedAction] = None