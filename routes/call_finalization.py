from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, model_validator
from typing import Optional
from functions.call_service import CallService
from auth import verify_api_key_header
import os
import json

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
    reason: str  # mc_incorrecto, no_acuerdo_precio, no_interesado, acuerdo_cerrado
    transcript: str

    @model_validator(mode='after')
    def check_load_id_for_reason(self):
        if self.reason not in ['mc_incorrecto', 'acuerdo_cerrado'] and not self.load_id:
            raise ValueError('load_id is required unless reason is mc_incorrecto or acuerdo_cerrado')
        return self

@router.post("/save_deal")
async def save_deal(
    request_body: CallFinalizationRequest,
    user_info: dict = Depends(verify_api_key_header),
    request: Request = None
):
    if request is not None:
        print("Headers received in /save_deal:", dict(request.headers))
    try:
        call_service = CallService()
        result = await call_service.process_call_finalization(request_body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving deal: {str(e)}")

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

@router.get("/get_calls")
async def get_calls(user_info: dict = Depends(verify_api_key_header)):
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
    calls = []
    stats = {
        "total_calls": 0,
        "total_deals": 0,
        "total_no_deals": 0,
        "reasons": {},
        "avg_final_price": None,
        "avg_negotiation_rounds": None
    }
    final_prices = []
    negotiation_rounds = []
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(temp_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        calls.append(data)
                        
                        # Check if this is a deal (has final_price) or no-deal (has reason)
                        if "reason" in data:
                            # This is a no-deal call
                            stats["total_no_deals"] += 1
                            reason = data.get("reason")
                            if reason:
                                stats["reasons"].setdefault(reason, 0)
                                stats["reasons"][reason] += 1
                        elif "final_price" in data:
                            # This is a successful deal
                            stats["total_deals"] += 1
                            price = data.get("final_price")
                            rounds = data.get("negotiation_rounds")
                            try:
                                if price is not None:
                                    final_prices.append(float(price))
                            except Exception:
                                pass
                            try:
                                if rounds is not None:
                                    negotiation_rounds.append(int(rounds))
                            except Exception:
                                pass
                        
                except Exception as e:
                    print(f"[WARN] Could not read {filename}: {e}")
    except FileNotFoundError:
        print(f"[WARN] Temp directory not found: {temp_dir}")
    
    stats["total_calls"] = stats["total_deals"] + stats["total_no_deals"]
    if final_prices:
        stats["avg_final_price"] = round(sum(final_prices) / len(final_prices), 2)
    if negotiation_rounds:
        stats["avg_negotiation_rounds"] = round(sum(negotiation_rounds) / len(negotiation_rounds), 2)
    
    return {"calls": calls, "stats": stats} 