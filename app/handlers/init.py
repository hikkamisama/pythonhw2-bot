from .base import base_router
from .setup import setup_router
from .admin import admin_router
from .water import water_router
from .food.handlers import food_router
from .workout.handlers import workout_router
from .progress import progress_router

routers = [
    base_router,
    setup_router,
    admin_router,
    water_router,
    food_router,
    workout_router,
    progress_router
]