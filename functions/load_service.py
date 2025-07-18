import random
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from num2words import num2words

class LoadService:
    """Service for handling load management and selection"""
    
    def __init__(self):
        self.mock_loads = self._generate_mock_loads()

    def euros_a_texto(euros: int) -> str:
        texto = num2words(euros, lang='es')
        return f"{texto} euros"
    
    def _generate_mock_loads(self) -> list:
        """Generate mock load data for demonstration"""
        equipment_types = ["Caja Seca", "Refrigerado", "Plataforma", "Step Deck", "Contenedor"]
        origins = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Zaragoza", "Alicante"]
        destinations = ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga", "Zaragoza", "Alicante", "Murcia", "Palma de Mallorca"]
        commodities = ["Electrónicos", "Productos Alimenticios", "Maquinaria", "Textiles", "Productos Químicos", "Automóviles", "Farmacéuticos", "Construcción"]
        
        loads = []
        for i in range(1, 21):  # Generate 20 mock loads
            pickup_date = datetime.now() + timedelta(days=random.randint(1, 7))
            delivery_date = pickup_date + timedelta(days=random.randint(1, 3))
            loadboard_rate = random.randint(1800, 3500)
            loadboard_rate_text = self.euros_to_text(loadboard_rate)
            loadboard_max_rate = loadboard_rate + random.randint(100, 500)
            loadboard_max_rate_text = self.euros_to_text(loadboard_max_rate)

            load = {
                "load_id": f"L{1000 + i}",
                "origin": random.choice(origins),
                "destination": random.choice(destinations),
                "pickup_datetime": pickup_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "delivery_datetime": delivery_date.strftime("%Y-%m-%dT%H:%M:%S"),
                "equipment_type": random.choice(equipment_types),
                "loadboard_rate": loadboard_rate,
                "loadboard_rate_text": loadboard_rate_text,
                "loadboard_max_rate": loadboard_max_rate,
                "loadboard_max_rate_text": loadboard_max_rate_text,
                "notes": "Easy dock access",
                "weight": random.randint(25000, 45000),
                "commodity_type": random.choice(commodities),
                "num_of_pieces": random.randint(10, 50),
                "miles": random.randint(500, 1200),
                "dimensions": "48x40x60"
            }
            loads.append(load)
        
        return loads
    
    async def get_best_available_load(self, equipment_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the best available load based on equipment type or random selection
        
        Args:
            equipment_type (Optional[str]): Type of equipment/truck
            
        Returns:
            Dict[str, Any]: Load information
        """
        try:
            # Simulate API delay
            await asyncio.sleep(0.1)
            
            available_loads = self.mock_loads.copy()
            
            if equipment_type:
                # Filter loads by equipment type
                filtered_loads = [
                    load for load in available_loads 
                    if load["equipment_type"].lower() == equipment_type.lower()
                ]
                
                if filtered_loads:
                    # Return the best load (highest rate) for the equipment type
                    best_load = max(filtered_loads, key=lambda x: x["loadboard_rate"])
                    return best_load
                else:
                    # No loads found for specific equipment type, return random load
                    return random.choice(available_loads)
            else:
                # Return random load if no equipment type specified
                return random.choice(available_loads)
                
        except Exception as e:
            # Return a default load in case of error
            return {
                "load_id": "L123",
                "origin": "Dallas, TX",
                "destination": "Atlanta, GA",
                "pickup_datetime": "2025-07-18T10:00:00",
                "delivery_datetime": "2025-07-19T18:00:00",
                "equipment_type": "Caja Seca",
                "loadboard_rate": 2200,
                "notes": "Acceso fácil al muelle",
                "weight": 35000,
                "commodity_type": "Electrónicos",
                "num_of_pieces": 20,
                "miles": 800,
                "dimensions": "48x40x60"
            }
    