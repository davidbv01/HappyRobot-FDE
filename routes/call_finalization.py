from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
from functions.call_service import CallService
from auth import verify_api_key_header

router = APIRouter()

class CallFinalizationRequest(BaseModel):
    mc_number: str
    company_name: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    load_id: str
    initial_offer: Optional[str] = None
    final_price: str
    negotiation_rounds: str
    transcript: str

class CallNoDealRequest(BaseModel):
    mc_number: str
    company_name: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    load_id: str
    reason: str  # e.g. mc incorrecto, no se ha llegado a un acuerdo en precio, no le interesaba
    transcript: str

@router.post("/finalize_call")
async def finalize_call(
    request_body: CallFinalizationRequest,
    user_info: dict = Depends(verify_api_key_header),
    request: Request = None
):
    if request is not None:
        print("Headers received in /finalize_call:", dict(request.headers))
    try:
        call_service = CallService()
        result = await call_service.process_call_finalization(request_body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizing call: {str(e)}")

@router.post("/finalize_call_no_deal")
async def finalize_call_no_deal(
    request_body: CallNoDealRequest,
    user_info: dict = Depends(verify_api_key_header),
    request: Request = None
):
    if request is not None:
        print("Headers received in /finalize_call_no_deal:", dict(request.headers))
    try:
        call_service = CallService()
        result = await call_service.process_call_no_deal(request_body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finalizing call (no deal): {str(e)}") 