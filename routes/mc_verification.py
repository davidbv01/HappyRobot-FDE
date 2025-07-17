from fastapi import APIRouter, HTTPException, Query, Depends
from functions.mc_service import MCService
from auth import verify_api_key_header

router = APIRouter()

@router.get("/verify_mc")
async def verify_mc(
    mc_number: str = Query(..., description="MC Number del carrier"),
    user_info: dict = Depends(verify_api_key_header)
):
    """
    Verifica si el MC Number está autorizado a operar, consultando la FMCSA API.
    
    Args:
        mc_number (str): MC Number del carrier
    
    Returns:
        dict: Información de validación del MC Number
    """
    try:
        mc_service = MCService()
        result = await mc_service.verify_mc_number(mc_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying MC number: {str(e)}") 