from pydantic import BaseModel, EmailStr

class PlayerBase(BaseModel):
    name: str
    nickname: str
    email: EmailStr

class PlayerCreate(PlayerBase):
    pass

class PlayerOut(PlayerBase):
    id: int

    class Config:
        from_attributes = True
