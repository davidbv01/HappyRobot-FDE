from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from functions.load_service import LoadService
from auth import verify_api_key_header

router = APIRouter()

@router.get("/loads/best")
async def get_best_load(
    equipment_type: Optional[str] = Query(None, description="Tipo de camión"),
    user_info: dict = Depends(verify_api_key_header)
):
    """
    Devuelve una carga disponible adecuada según el tipo de camión o de forma aleatoria si no se especifica.
    
    Args:
        equipment_type (Optional[str]): Tipo de camión
    
    Returns:
        dict: Información de la carga disponible
    """
    try:
        load_service = LoadService()
        result = await load_service.get_best_available_load(equipment_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting best load: {str(e)}") 