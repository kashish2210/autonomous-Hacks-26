# claim_verifier_schema.py
from pydantic import BaseModel, Field
from typing import List, Literal


class VerificationResult(BaseModel):
    verdict: Literal[
        "VERIFIED",
        "FALSE",
        "PARTIALLY_VERIFIED",
        "UNVERIFIABLE"
    ] = Field(description="Final factual verdict")

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )

    reasoning: str = Field(
        description="Short factual reasoning based on evidence"
    )

    evidence_sources: List[str] = Field(
        description="List of URLs or source names"
    )
