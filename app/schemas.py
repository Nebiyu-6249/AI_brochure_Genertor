from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class BrochureRequest(BaseModel):
    company_name: str = Field(..., min_length=1)
    website_url: str = Field(..., min_length=5)
    tone: str = "professional"  # e.g. professional, friendly, investor, recruiting


class BrochureResponse(BaseModel):
    brochure_markdown: str
    brochure_html: str
    sources: List[str]
