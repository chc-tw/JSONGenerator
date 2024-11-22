from fastapi import APIRouter
from pydantic import BaseModel
from .JSONGenerator import generateJSON

class Prompt(BaseModel):
    user_prompt: str
    key : str
class Response(BaseModel):
    system_response: dict

router = APIRouter(prefix="/strategy")

@router.post("/")
async def generate_schema(prompt: Prompt):
    result = await generateJSON(prompt.user_prompt, prompt.key)
    return {"schema": result}
