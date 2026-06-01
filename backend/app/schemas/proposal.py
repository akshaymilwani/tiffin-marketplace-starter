from pydantic import BaseModel
from typing import Optional

class ProposalCreate(BaseModel):
    request_id: str
    business_id: str
    quote_amount: float
    eta_notes: Optional[str] = None
    message: Optional[str] = None
