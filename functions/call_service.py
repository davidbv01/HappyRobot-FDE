import asyncio
import random
from typing import Dict, Any
from datetime import datetime

class CallService:
    """Service for handling call finalization and analysis"""
    
    def __init__(self):
        self.sentiment_keywords = {
            "positive": ["great", "excellent", "perfect", "good", "satisfied", "happy", "pleased"],
            "negative": ["bad", "terrible", "awful", "disappointed", "angry", "frustrated", "unsatisfied"],
            "neutral": ["okay", "fine", "acceptable", "standard", "normal", "regular"]
        }
    
    async def process_call_finalization(self, call_data) -> Dict[str, Any]:
        """
        Process and analyze call finalization data
        
        Args:
            call_data: CallFinalizationRequest object with call details
            
        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Simulate processing delay
            await asyncio.sleep(0.2)
            
            # Analyze sentiment from dialogue summary
            sentiment = self._analyze_sentiment(call_data.dialogue_summary)
            
            # Determine deal result based on final price and negotiation rounds
            deal_result = self._determine_deal_result(
                call_data.final_price, 
                call_data.negotiation_rounds,
                call_data.dialogue_summary
            )
            
            # Create summary
            summary = {
                "mc_number": call_data.mc_number,
                "load_id": call_data.load_id,
                "price_agreed": call_data.final_price,
                "rounds": call_data.negotiation_rounds,
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
                    "price_agreed": call_data.final_price,
                    "rounds": call_data.negotiation_rounds,
                    "error": str(e)
                }
            }
    
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
    
    def _determine_deal_result(self, final_price: float, negotiation_rounds: int, dialogue_summary: str) -> str:
        """
        Determine the result of the deal based on various factors
        
        Args:
            final_price (float): Final agreed price
            negotiation_rounds (int): Number of negotiation rounds
            dialogue_summary (str): Summary of the dialogue
            
        Returns:
            str: Deal result (deal_closed, deal_pending, deal_rejected)
        """
        dialogue_lower = dialogue_summary.lower()
        
        # Keywords that indicate deal closure
        closure_keywords = ["accepted", "agreed", "deal", "confirmed", "yes", "okay"]
        rejection_keywords = ["rejected", "declined", "no", "refused", "cancelled"]
        
        has_closure_indicators = any(keyword in dialogue_lower for keyword in closure_keywords)
        has_rejection_indicators = any(keyword in dialogue_lower for keyword in rejection_keywords)
        
        if has_rejection_indicators:
            return "deal_rejected"
        elif has_closure_indicators and final_price > 0:
            return "deal_closed"
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
        
        if "rate" in dialogue_lower or "price" in dialogue_lower:
            key_points.append("Price negotiation occurred")
        
        if "time" in dialogue_lower or "schedule" in dialogue_lower:
            key_points.append("Timing discussed")
        
        if "equipment" in dialogue_lower or "truck" in dialogue_lower:
            key_points.append("Equipment requirements mentioned")
        
        if "delivery" in dialogue_lower or "pickup" in dialogue_lower:
            key_points.append("Logistics details covered")
        
        if not key_points:
            key_points.append("Standard negotiation")
        
        return key_points 