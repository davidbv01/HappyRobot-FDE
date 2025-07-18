import asyncio
import random
from typing import Dict, Any
from datetime import datetime
import os
import json

class CallService:
    """Service for handling call finalization and analysis"""
    
    def __init__(self):
        self.temp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def process_call_finalization(self, call_data) -> Dict[str, Any]:
        """
        Process and analyze call finalization data
        
        Args:
            call_data: CallFinalizationRequest object with call details
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Save the input JSON to a file in /temp
            await self._save_json_to_file(call_data)
            
            # Simulate processing delay
            await asyncio.sleep(0.2)
            
            # Convert string fields to appropriate types for analysis
            try:
                final_price = float(call_data.final_price)
            except Exception:
                final_price = None
            try:
                negotiation_rounds = int(call_data.negotiation_rounds)
            except Exception:
                negotiation_rounds = None
            
            # Create summary
            summary = {
                "mc_number": call_data.mc_number,
                "company_name": call_data.company_name,
                "origin": call_data.origin,
                "destination": call_data.destination,
                "pickup_datetime": call_data.pickup_datetime,
                "delivery_datetime": call_data.delivery_datetime,
                "load_id": call_data.load_id,
                "final_price": final_price,
                "negotiation_rounds": negotiation_rounds,
                "processed_at": datetime.now().isoformat(),
            }
            
            result = {
                "result": "saved",
                "summary": summary
            }
            
            return result
            
        except Exception as e:
            return {
                "result": "processing_error",
                "summary": {
                    "mc_number": getattr(call_data, "mc_number", None),
                    "load_id": getattr(call_data, "load_id", None),
                    "error": str(e)
                }
            }

    async def _save_json_to_file(self, call_data):
        """
        Save the call finalization JSON to a file in /temp with a unique filename
        """
        try:
            # Convert to dict if it's a Pydantic model
            if hasattr(call_data, 'dict'):
                data = call_data.dict()
            else:
                data = dict(call_data)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"call_{data.get('mc_number', 'unknown')}_{timestamp}.json"
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[WARN] Could not save call finalization JSON: {e}") 