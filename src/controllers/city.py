from src.controllers.crud import CRUD
from src.models import City


class CityController(CRUD):
    model = City
