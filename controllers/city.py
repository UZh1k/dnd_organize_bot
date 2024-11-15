from controllers.crud import CRUD
from models import City


class CityController(CRUD):
    model = City
