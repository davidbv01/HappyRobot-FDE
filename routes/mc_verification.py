from fastapi import APIRouter, HTTPException, Path, Depends, Request
from functions.mc_service import MCService
from auth import verify_api_key_header

router = APIRouter()

@router.get("/carriers/{mc_number}")
async def get_carrier(
    mc_number: str = Path(..., description="MC Number del carrier"),
    user_info: dict = Depends(verify_api_key_header),
    request: Request = None
):
    """
    Verifica si el MC Number está autorizado a operar, consultando la FMCSA API.
    """
    # Log the request base_url
    base_url = str(request.base_url) if request else None
    print(f"[BASE URL LOG] /carriers/{mc_number} called from base_url: {base_url}")
    try:
        mc_service = MCService()
        result = await mc_service.verify_mc_number(mc_number)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying MC number: {str(e)}") 