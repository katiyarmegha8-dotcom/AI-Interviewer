"""Pydantic models for curriculum data."""

from enum import Enum

from pydantic import BaseModel, Field


class DayType(str, Enum):
    """Day activity type as defined in the curriculum."""

    SETUP = "SETUP"
    BUILD = "BUILD"
    AI_CORE = "AI_CORE"
    LEARN = "LEARN"
    SHIP_IT = "SHIP_IT"
    OPTIMIZE = "OPTIMIZE"
    CAPSTONE = "CAPSTONE"


class Module(BaseModel):
    """A curriculum module spanning a range of days."""

    n: int = Field(description="Module number")
    title: str = Field(description="Module title")
    days: list[int] = Field(description="Start and end day of the module")


class CurriculumDay(BaseModel):
    """A single day within the curriculum."""

    day: int = Field(description="Day number")
    title: str = Field(description="Day title")
    type: DayType = Field(description="Activity type")
    tools: list[str] = Field(description="Tools and technologies used")
    objectives: list[str] = Field(description="Learning objectives for the day")


class Curriculum(BaseModel):
    """Top-level curriculum structure matching curriculum.json."""

    cohort: str = Field(description="Cohort description")
    modules: list[Module] = Field(description="Curriculum modules")
    days: list[CurriculumDay] = Field(description="Day-by-day curriculum details")
