import asyncio
import random
from typing import Dict, Any
from datetime import datetime
import os
import json

class CallService:
    """Service for handling call finalization and analysis"""
    
    def __init__(self):
        self.sentiment_keywords = {
            "positive": ["great", "excellent", "perfect", "good", "satisfied", "happy", "pleased", "aceptó", "vale", "ok", "sí"],
            "negative": ["bad", "terrible", "awful", "disappointed", "angry", "frustrated", "unsatisfied", "no", "rechazó", "cancelado"],
            "neutral": ["okay", "fine", "acceptable", "standard", "normal", "regular"]
        }
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
            
            # Analyze sentiment from dialogue summary
            sentiment = self._analyze_sentiment(call_data.dialogue_summary)
            
            # Determine deal result based on deal_accepted and negotiation rounds
            deal_result = self._determine_deal_result(
                call_data.final_price, 
                call_data.negotiation_rounds,
                call_data.dialogue_summary,
                call_data.deal_accepted
            )
            
            # Create summary
            summary = {
                "mc_number": call_data.mc_number,
                "load_id": call_data.load_id,
                "initial_offer": call_data.initial_offer,
                "price_agreed": call_data.final_price,
                "rounds": call_data.negotiation_rounds,
                "deal_accepted": call_data.deal_accepted,
                "processed_at": datetime.now().isoformat(),
                "company_name": call_data.company_name
            }
            
            result = {
                "result": deal_result,
                "sentiment": sentiment,
                "summary": summary,
                "analysis": {
                    "dialogue_length": len(call_data.dialogue_summary),
                    "transcript_length": len(call_data.transcript),
                    "negotiation_intensity": self._calculate_negotiation_intensity(call_data.negotiation_rounds),
                    "key_points": self._extract_key_points(call_data.dialogue_summary)
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "result": "processing_error",
                "sentiment": "neutral",
                "summary": {
                    "mc_number": call_data.mc_number,
                    "load_id": call_data.load_id,
                    "initial_offer": getattr(call_data, "initial_offer", None),
                    "price_agreed": call_data.final_price,
                    "rounds": call_data.negotiation_rounds,
                    "deal_accepted": getattr(call_data, "deal_accepted", None),
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
    
    def _analyze_sentiment(self, dialogue_summary: str) -> str:
        """
        Analyze sentiment from dialogue summary
        
        Args:
            dialogue_summary (str): Summary of the dialogue
            
        Returns:
            str: Sentiment classification (positive, negative, neutral)
        """
        dialogue_lower = dialogue_summary.lower()
        
        positive_count = sum(1 for word in self.sentiment_keywords["positive"] if word in dialogue_lower)
        negative_count = sum(1 for word in self.sentiment_keywords["negative"] if word in dialogue_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _determine_deal_result(self, final_price: float, negotiation_rounds: int, dialogue_summary: str, deal_accepted: bool) -> str:
        """
        Determine the result of the deal based on various factors
        
        Args:
            final_price (float): Final agreed price
            negotiation_rounds (int): Number of negotiation rounds
            dialogue_summary (str): Summary of the dialogue
            deal_accepted (bool): Whether the deal was accepted
            
        Returns:
            str: Deal result (deal_closed, deal_pending, deal_rejected)
        """
        dialogue_lower = dialogue_summary.lower()
        
        # Keywords that indicate deal closure
        closure_keywords = ["accepted", "agreed", "deal", "confirmed", "yes", "okay", "aceptó", "vale", "ok", "sí"]
        rejection_keywords = ["rejected", "declined", "no", "refused", "cancelled", "rechazó", "cancelado"]
        
        has_closure_indicators = any(keyword in dialogue_lower for keyword in closure_keywords)
        has_rejection_indicators = any(keyword in dialogue_lower for keyword in rejection_keywords)
        
        if deal_accepted or (has_closure_indicators and final_price > 0):
            return "deal_closed"
        elif has_rejection_indicators or (deal_accepted is False):
            return "deal_rejected"
        elif negotiation_rounds > 5:
            return "deal_pending"  # Too many rounds might indicate complications
        else:
            return "deal_closed"  # Default to closed if price is agreed
    
    def _calculate_negotiation_intensity(self, rounds: int) -> str:
        """
        Calculate negotiation intensity based on number of rounds
        
        Args:
            rounds (int): Number of negotiation rounds
            
        Returns:
            str: Intensity level (low, medium, high)
        """
        if rounds <= 2:
            return "low"
        elif rounds <= 4:
            return "medium"
        else:
            return "high"
    
    def _extract_key_points(self, dialogue_summary: str) -> list:
        """
        Extract key points from dialogue summary
        
        Args:
            dialogue_summary (str): Summary of the dialogue
            
        Returns:
            list: List of key points
        """
        key_points = []
        
        dialogue_lower = dialogue_summary.lower()
        
        if "rate" in dialogue_lower or "price" in dialogue_lower or "oferta" in dialogue_lower:
            key_points.append("Negociación de precio/oferta")
        
        if "time" in dialogue_lower or "schedule" in dialogue_lower or "hora" in dialogue_lower:
            key_points.append("Discusión de tiempos")
        
        if "equipment" in dialogue_lower or "truck" in dialogue_lower or "camión" in dialogue_lower:
            key_points.append("Requisitos de equipo")
        
        if "delivery" in dialogue_lower or "pickup" in dialogue_lower or "entrega" in dialogue_lower or "recogida" in dialogue_lower:
            key_points.append("Detalles logísticos")
        
        if not key_points:
            key_points.append("Negociación estándar")
        
        return key_points 