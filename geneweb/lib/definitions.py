# Copyright (c) 1998-2007 INRIA
# Python rewrite of Geneweb def module

from enum import Enum, IntEnum
from typing import Union, Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

class HttpStatus(IntEnum):
    """Http response status"""
    OK = 200
    MOVED_TEMPORARILY = 302
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503

class HttpException(Exception):
    def __init__(self, status: HttpStatus, message: str):
        self.status = status
        self.message = message
        super().__init__(f"{status}: {message}")

class Calendar(Enum):
    """Calendar types"""
    GREGORIAN = "gregorian"
    JULIAN = "julian"
    FRENCH = "french"
    HEBREW = "hebrew"

class Precision(Enum):
    """Date precision"""
    SURE = "sure"
    ABOUT = "about"
    MAYBE = "maybe"
    BEFORE = "before"
    AFTER = "after"
    OR_YEAR = "or_year"
    YEAR_INT = "year_int"

@dataclass
class Dmy2:
    """Date range"""
    day2: int
    month2: int
    year2: int
    delta2: int

@dataclass
class Dmy:
    """Date with precision"""
    day: int
    month: int
    year: int
    prec: Precision
    delta: int

class Date:
    """Date representation"""
    def __init__(self, dmy: Optional[Dmy] = None, calendar: Calendar = Calendar.GREGORIAN, text: Optional[str] = None):
        if text:
            self.text = text
            self.dmy = None
            self.calendar = None
        else:
            self.dmy = dmy
            self.calendar = calendar
            self.text = None
    
    def is_text(self) -> bool:
        return self.text is not None

class CDate:
    """Compact date"""
    def __init__(self, value: Union[int, str, Date, None] = None, calendar: Calendar = Calendar.GREGORIAN):
        if value is None:
            self.type = "none"
            self.value = None
        elif isinstance(value, str):
            self.type = "text"
            self.value = value
        elif isinstance(value, Date):
            self.type = "date"
            self.value = value
        elif isinstance(value, int):
            self.type = calendar.value
            self.value = value
        self.calendar = calendar

class RelationKind(Enum):
    """Relation kind between couple"""
    MARRIED = "married"
    NOT_MARRIED = "not_married"
    ENGAGED = "engaged"
    NO_SEXES_CHECK_NOT_MARRIED = "no_sexes_check_not_married"
    NO_MENTION = "no_mention"
    NO_SEXES_CHECK_MARRIED = "no_sexes_check_married"
    MARRIAGE_BANN = "marriage_bann"
    MARRIAGE_CONTRACT = "marriage_contract"
    MARRIAGE_LICENSE = "marriage_license"
    PACS = "pacs"
    RESIDENCE = "residence"

class DivorceStatus(Enum):
    """Divorce status"""
    NOT_DIVORCED = "not_divorced"
    DIVORCED = "divorced"
    SEPARATED_OLD = "separated_old"
    NOT_SEPARATED = "not_separated"
    SEPARATED = "separated"

@dataclass
class Divorce:
    status: DivorceStatus
    date: Optional[CDate] = None

class DeathReason(Enum):
    """Death reason"""
    KILLED = "killed"
    MURDERED = "murdered"
    EXECUTED = "executed"
    DISAPPEARED = "disappeared"
    UNSPECIFIED = "unspecified"

class DeathStatus(Enum):
    """Death status"""
    NOT_DEAD = "not_dead"
    DEATH = "death"
    DEAD_YOUNG = "dead_young"
    DEAD_DONT_KNOW_WHEN = "dead_dont_know_when"
    DONT_KNOW_IF_DEAD = "dont_know_if_dead"
    OF_COURSE_DEAD = "of_course_dead"

@dataclass
class Death:
    status: DeathStatus
    reason: Optional[DeathReason] = None
    date: Optional[CDate] = None

class BurialType(Enum):
    """Burial type"""
    UNKNOWN = "unknown"
    BURIED = "buried"
    CREMATED = "cremated"

@dataclass
class Burial:
    type: BurialType
    date: Optional[CDate] = None

class Access(Enum):
    """Access rights"""
    IF_TITLES = "if_titles"
    PUBLIC = "public"
    SEMI_PUBLIC = "semi_public"
    PRIVATE = "private"

class Sex(Enum):
    """Gender"""
    MALE = "male"
    FEMALE = "female"
    NEUTER = "neuter"

@dataclass
class Person:
    """Person data structure"""
    first_name: str = ""
    surname: str = ""
    occ: int = 0
    image: str = ""
    public_name: str = ""
    qualifiers: List[str] = None
    aliases: List[str] = None
    first_names_aliases: List[str] = None
    surnames_aliases: List[str] = None
    titles: List['Title'] = None
    rparents: List['RelatedPerson'] = None
    related: List['RelatedPerson'] = None
    occupation: str = ""
    sex: Sex = Sex.NEUTER
    access: Access = Access.PRIVATE
    birth: Optional[CDate] = None
    birth_place: str = ""
    birth_note: str = ""
    birth_src: str = ""
    baptism: Optional[CDate] = None
    baptism_place: str = ""
    baptism_note: str = ""
    baptism_src: str = ""
    death: Death = None
    death_place: str = ""
    death_note: str = ""
    death_src: str = ""
    burial: Burial = None
    burial_place: str = ""
    burial_note: str = ""
    burial_src: str = ""
    notes: str = ""
    psources: str = ""
    key_index: int = -1
    
    def __post_init__(self):
        if self.qualifiers is None:
            self.qualifiers = []
        if self.aliases is None:
            self.aliases = []
        if self.first_names_aliases is None:
            self.first_names_aliases = []
        if self.surnames_aliases is None:
            self.surnames_aliases = []
        if self.titles is None:
            self.titles = []
        if self.rparents is None:
            self.rparents = []
        if self.related is None:
            self.related = []
        if self.death is None:
            self.death = Death(DeathStatus.DONT_KNOW_IF_DEAD)
        if self.burial is None:
            self.burial = Burial(BurialType.UNKNOWN)

@dataclass
class Family:
    """Family data structure"""
    marriage: Optional[CDate] = None
    marriage_place: str = ""
    marriage_note: str = ""
    marriage_src: str = ""
    witnesses: List[int] = None
    relation: RelationKind = RelationKind.MARRIED
    divorce: Divorce = None
    comment: str = ""
    origin_file: str = ""
    fsources: str = ""
    fam_index: int = -1
    
    def __post_init__(self):
        if self.witnesses is None:
            self.witnesses = []
        if self.divorce is None:
            self.divorce = Divorce(DivorceStatus.NOT_DIVORCED)

@dataclass
class Title:
    """Title information"""
    name: str = ""
    title: str = ""
    fief: str = ""
    date_start: Optional[CDate] = None
    date_end: Optional[CDate] = None
    nth: int = 0

@dataclass
class RelatedPerson:
    """Related person reference"""
    person_id: int
    relation_type: str
