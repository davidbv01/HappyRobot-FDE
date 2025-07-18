from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, root_validator
from typing import Optional
from functions.call_service import CallService
from auth import verify_api_key_header

router = APIRouter()

class CallFinalizationRequest(BaseModel):
    mc_number: str
    company_name: str
    load_id: str
    initial_offer: Optional[str] = None
    final_price: str
    negotiation_rounds: str
    transcript: str

class CallNoDealRequest(BaseModel):
    mc_number: str
    company_name: str
    load_id: Optional[str] = None
    reason: str  # mc_incorrecto, no_acuerdo_precio, no_interesado
    transcript: str

    @root_validator
    def check_load_id_for_reason(cls, values):
        reason = values.get('reason')
        load_id = values.get('load_id')
        if reason != 'mc_incorrecto' and not load_id:
            raise ValueError('load_id is required unless reason is mc_incorrecto')
        return values

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