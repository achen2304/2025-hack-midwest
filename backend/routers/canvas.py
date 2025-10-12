from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CanvasToken(BaseModel):
    token: str

@router.post("/canvas/token")
async def update_canvas_token(canvas_token: CanvasToken):
    try:
        # Here, you would typically save the token to a database or perform other processing
        # For now, we'll just log it
        print(f"Received Canvas token: {canvas_token.token}")
        return {"message": "Canvas token updated successfully"}
    except Exception as e:
        print(f"Error updating Canvas token: {e}")
        raise HTTPException(status_code=500, detail="Failed to update Canvas token")