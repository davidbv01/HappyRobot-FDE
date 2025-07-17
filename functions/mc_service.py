import httpx
import asyncio
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MCService:
    """Service for handling MC Number verification with FMCSA API"""
    
    def __init__(self):
        self.fmcsa_base_url = "https://mobile.fmcsa.dot.gov/qc/services/carriers"
        self.fmcsa_api_key = os.getenv("FMCSA_API_KEY")
        
    async def verify_mc_number(self, mc_number: str) -> Dict[str, Any]:
        """
        Verify MC Number with FMCSA API
        
        Args:
            mc_number (str): The MC number to verify
            
        Returns:
            Dict[str, Any]: Verification result
        """
        try:
            # Check if API key is configured
            if not self.fmcsa_api_key:
                return {
                    "valid": False,
                    "reason": "FMCSA API key not configured. Please set FMCSA_API_KEY in .env file"
                }
            
            # Make actual API call to FMCSA
            api_response = await self._call_fmcsa_api(mc_number)
            
            if "error" in api_response:
                return {
                    "valid": False,
                    "reason": f"FMCSA API error: {api_response['error']}"
                }
            
            # Parse the response
            return self._parse_fmcsa_response(api_response, mc_number)
                
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Error verifying MC number: {str(e)}"
            }
    
    def _parse_fmcsa_response(self, api_response: Dict[str, Any], mc_number: str) -> Dict[str, Any]:
        """
        Parse FMCSA API response to extract relevant information
        
        Args:
            api_response: Raw response from FMCSA API
            mc_number: Original MC number being verified
            
        Returns:
            Dict[str, Any]: Parsed verification result
        """
        try:
            # Check if content exists and has data
            if not api_response.get("content") or len(api_response["content"]) == 0:
                return {
                    "valid": False,
                    "reason": "MC number not found in FMCSA database"
                }
            
            # Get the first carrier record
            carrier_data = api_response["content"][0].get("carrier", {})
            
            # Check if carrier is allowed to operate
            allowed_to_operate = carrier_data.get("allowedToOperate", "N")
            status_code = carrier_data.get("statusCode", "I")
            
            # Determine if carrier is active
            is_active = allowed_to_operate == "Y" and status_code == "A"
            
            if not is_active:
                return {
                    "valid": False,
                    "reason": f"Carrier not authorized to operate. Status: {status_code}, Allowed: {allowed_to_operate}"
                }
            
            # Extract company information
            company_name = carrier_data.get("legalName") or carrier_data.get("dbaName") or "Unknown Company"
            
            return {
                "valid": True,
                "company_name": company_name,
                "status": "Active",
                "dot_number": carrier_data.get("dotNumber"),
                "ein": carrier_data.get("ein"),
                "carrier_operation": carrier_data.get("carrierOperation", {}).get("carrierOperationDesc"),
                "phy_city": carrier_data.get("phyCity"),
                "phy_state": carrier_data.get("phyState"),
                "safety_rating": carrier_data.get("safetyRating"),
                "total_drivers": carrier_data.get("totalDrivers"),
                "total_power_units": carrier_data.get("totalPowerUnits")
            }
            
        except Exception as e:
            return {
                "valid": False,
                "reason": f"Error parsing FMCSA response: {str(e)}"
            }
    
    async def _call_fmcsa_api(self, mc_number: str) -> Dict[str, Any]:
        """
        Make actual call to FMCSA API
        
        Args:
            mc_number (str): MC number to verify
            
        Returns:
            Dict[str, Any]: API response
        """
        url = f"{self.fmcsa_base_url}/docket-number/{mc_number}?webKey={self.fmcsa_api_key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"error": "MC number not found in FMCSA database"}
                elif response.status_code == 401:
                    return {"error": "Invalid FMCSA API key"}
                elif response.status_code == 403:
                    return {"error": "Access denied to FMCSA API"}
                else:
                    return {"error": f"FMCSA API returned status code: {response.status_code}"}
                    
            except httpx.TimeoutException:
                return {"error": "FMCSA API request timed out"}
            except httpx.RequestError as e:
                return {"error": f"Network error: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"} 