from typing import Optional

from pydantic import BaseModel, Field


class Contract(BaseModel):
    address: str = Field(alias="_id")
    name: Optional[str]
    symbol: Optional[str]
    contract_type: str = Field(alias="type")

    class Config:
        allow_population_by_field_name = True


class Nft(BaseModel):
    contract_id: str
    token_id: int
    token_uri: Optional[str]


class Transfer(BaseModel):
    nft_id: str
    transaction_hash: str = Field(alias="_id")
    transfer_from: str = Field(alias="from")
    transfer_to: str = Field(alias="to")

    class Config:
        allow_population_by_field_name = True
