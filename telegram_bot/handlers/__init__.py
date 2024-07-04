from aiogram import Router

from .auth import router as auth_router
from .user import router as user_router
from .tasks import router as tasks_router
from .admin import router as admin_router

router = Router()
router.include_router(auth_router)
router.include_router(user_router)
router.include_router(tasks_router)
router.include_router(admin_router)
