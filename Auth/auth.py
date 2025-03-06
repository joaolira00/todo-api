from fastapi import APIRouter

router = APIRouter()

@router.get("/auth", tags=["Auth"])
async def get_user():
    return {"user": "authenticated"}