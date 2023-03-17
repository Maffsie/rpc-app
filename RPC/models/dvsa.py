from enum import Enum, auto

from requests import Response

from RPC.util.coercion import coerce_type

from .dvla import FuelType, acronym_mfrs


class DVSAError:
    major: int = None
    minor: int = None
    reason: str = None
    detail: str = None
    _j: dict = None

    def __init__(self, resp: Response):
        self.major = resp.status_code
        match resp.status_code:
            case 403:
                self.reason = (
                    "Unable to look up registration number due to an API error. The DVSA responded "
                    "Forbidden, which is not a temporary problem. Please contact @Maffsie."
                )
                return
            case 404:
                self.reason = (
                    "Registration number is in a valid format, but was not recognised by the DVSA. "
                    "If you know this to be a previously valid and registered registration number, "
                    "the vehicle may have been scrapped, or the number may have been removed from "
                    "a specific vehicle."
                )
                return
        self._j = resp.json()
        self.major = self._j["errors"][0]["status"]
        self.minor = self._j["errors"][0]["code"]
        self.reason = self._j["errors"][0]["title"]
        self.detail = self._j["errors"][0]["detail"]

    def as_view(self):
        return str(self)

    def __str__(self):
        if not self.minor:
            return f"{self.reason} ({self.major})"
        return f"{self.major}.{self.minor} {self.reason}: {self.detail}"

    def __repr__(self):
        if not self.minor:
            return f"<DVLAError {self.major}>"
        return f"<DVLAError {self.major}.{self.minor} [{self.reason} [{self.detail}]]>"


class MOTResult(Enum):
    Passed = "pass"
    Failed = "fail"


class OdometerUnit(Enum):
    mi = "Mile"
    km = "Kilometer"


class MOTHistoryCommentType(Enum):
    User_Entered = "User-entered"
    Advisory = "Advisory note"
    Fail = "Failure"


class MOTHistoryComment:
    comment: str = None
    ctype: MOTHistoryCommentType = None

    def __init__(self, comment: dict):
        self.comment = comment["text"]
        self.ctype = coerce_type(comment["type"], MOTHistoryCommentType)

    @property
    def str(self) -> str:
        return f"*{self.ctype.value}* - {self.comment}"

    @property
    def str_bullet(self) -> str:
        return f"- {self.str}\n"


class MOTHistoryEntry:
    result: MOTResult = None
    dt_completed: str = None
    dt_completed_date: str = None
    dt_completed_year: int = None
    dt_completed_month: int = None
    dt_completed_day: int = None
    dt_completed_time: str = None
    dt_completed_hour: int = None
    dt_completed_minute: int = None
    dt_completed_second: int = None
    dt_expiry: str = None
    dt_expiry_year: int = None
    dt_expiry_month: int = None
    dt_expiry_day: int = None
    odometer_val: int = None
    odometer_unit: OdometerUnit = None
    test_num: int = None
    comments: list[MOTHistoryComment] = None

    def __init__(self, entry: dict):
        self.result = coerce_type(entry["testResult"], MOTResult)
        self.dt_completed = entry["completedDate"]
        self.dt_completed_date, self.dt_completed_time = self.dt_completed.split(" ")
        (
            self.dt_completed_year,
            self.dt_completed_month,
            self.dt_completed_day,
        ) = self.dt_completed_date.split(".")
        (
            self.dt_completed_hour,
            self.dt_completed_minute,
            self.dt_completed_second,
        ) = self.dt_completed_time.split(":")
        self.dt_expiry = entry["expiryDate"]
        (
            self.dt_expiry_year,
            self.dt_expiry_month,
            self.dt_expiry_day,
        ) = self.dt_expiry.split(".")

        self.dt_completed_year = coerce_type(self.dt_completed_year, int)
        self.dt_completed_month = coerce_type(self.dt_completed_month, int)
        self.dt_completed_day = coerce_type(self.dt_completed_day, int)
        self.dt_completed_hour = coerce_type(self.dt_completed_hour, int)
        self.dt_completed_minute = coerce_type(self.dt_completed_minute, int)
        self.dt_completed_second = coerce_type(self.dt_completed_second, int)
        self.dt_expiry_year = coerce_type(self.dt_expiry_year, int)
        self.dt_expiry_month = coerce_type(self.dt_expiry_month, int)
        self.dt_expiry_day = coerce_type(self.dt_expiry_day, int)
        self.test_num = coerce_type(entry["motTestNumber"], int)
        self.odometer_val = coerce_type(entry["odometerValue"], int)
        self.odometer_unit = coerce_type(entry["odometerUnit"], OdometerUnit)
        self.comments = []
        if entry.get("rfrAndComments", None) is not None:
            self.comments = [
                MOTHistoryComment(comment) for comment in entry["rfrAndComments"]
            ]

    @property
    def str(self) -> str:
        return (
            f"MOT #*{self.test_num}* was conducted on "
            f"*{self.dt_completed_year}/{self.dt_completed_month:02d}/"
            f"{self.dt_completed_day:02d}*"
            f" at *{self.dt_completed_hour:02d}:{self.dt_completed_minute:02d}:"
            f"{self.dt_completed_second:02d}*."
            f"\nIt *{self.result.name.lower()}*{self.str_passed_expiry}.\n"
            f"At time of test, the odometer was recorded as *{self.odometer_val} "
            f"{self.odometer_unit.value.lower()}{'s' if self.odometer_val != 1 else ''}*.\n\n"
            f"{self.str_comments}"
        )

    @property
    def str_passed_expiry(self) -> str:
        if self.result is MOTResult.Failed:
            return ""
        return (
            f", and will require a new MOT to be performed before *{self.dt_expiry_year}/"
            f"{self.dt_expiry_month:02d}/{self.dt_expiry_day:02d}*"
        )

    @property
    def str_comments(self) -> str:
        if len(self.comments) == 0:
            return "There were no notes included with this MOT result."
        return (
            "The following notes were included during the testing process:\n"
            f"{[comment.str_bullet for comment in self.comments]}"
        )


class DVSAVehicle:
    number: str = None
    manufacturer: str = None
    model: str = None
    year: int = None
    colour: str = None
    fuel: FuelType = None
    dvla_id: int = None
    dt_firstused: str = None
    dt_firstused_year: int = None
    dt_firstused_month: int = None
    dt_firstused_day: int = None
    dt_firstmot: str = None
    dt_firstmot_year: int = None
    dt_firstmot_month: int = None
    dt_firstmot_day: int = None
    tests: list[MOTHistoryEntry] = None

    def __init__(self, bjss_response: dict):
        self.manufacturer = bjss_response.get("make", "[Unknown make]").capitalize()
        if self.manufacturer.upper() in acronym_mfrs:
            self.manufacturer = self.manufacturer.upper()
        self.model = bjss_response.get("model", "[Unknown model]")
        self.fuel = coerce_type(bjss_response.get("fuelType", None), FuelType)
        self.year = coerce_type(bjss_response.get("manufactureYear", None), int)
        self.colour = bjss_response.get("primaryColour", None)
        self.dvla_id = coerce_type(bjss_response.get("dvlaId", None), int)
        self.number = bjss_response.get("registration", None)

        self.dt_firstused = bjss_response.get("firstUsedDate", None)
        self.dt_firstmot = bjss_response.get("motTestExpiryDate", None)

        # if the DVSA ever decide to change the format of this, we're fucked
        if self.dt_firstused is not None:
            sep = self.dt_firstused[4]
            (
                self.dt_firstused_year,
                self.dt_firstused_month,
                self.dt_firstused_day,
            ) = self.dt_firstused.split(sep)
            self.dt_firstused_year = coerce_type(self.dt_firstused_year, int)
            self.dt_firstused_month = coerce_type(self.dt_firstused_month, int)
            self.dt_firstused_day = coerce_type(self.dt_firstused_day, int)

        if self.dt_firstmot is not None:
            sep = self.dt_firstmot[4]
            (
                self.dt_firstmot_year,
                self.dt_firstmot_month,
                self.dt_firstmot_day,
            ) = self.dt_firstmot.split(sep)
            self.dt_firstmot_year = coerce_type(self.dt_firstmot_year, int)
            self.dt_firstmot_month = coerce_type(self.dt_firstmot_month, int)
            self.dt_firstmot_day = coerce_type(self.dt_firstmot_day, int)

        self.tests = []
        if bjss_response.get("motTests", None) is not None:
            self.tests = [MOTHistoryEntry(entry) for entry in bjss_response["motTests"]]

    @property
    def str_full(self):
        return (
            "*Basic information*\n"
            f"Vehicle with registration number *{self.number}* is a *{self.str_clryr} "
            f"{self.manufacturer} {self.model.capitalize()}*.\n\n"
            "*MOT history*"
            f"It has {self.str_fuel} engine{self.str_dvlaid}.\n"
            f"{self.str_firstmot_or_used}.{self.str_recent_test}"
        )

    @property
    def str_clryr(self) -> str:
        return (
            f"{self.colour + ' ' if self.colour is not None else ''}"
            f"{str(self.year) + ' ' if self.year is not None else ''}"
        )

    @property
    def str_dvlaid(self) -> str:
        if self.dvla_id is None:
            return ""
        return f", and is registered to the DVLA with ID *{self.dvla_id}*"

    @property
    def str_fuel(self) -> str:
        if isinstance(self.fuel, FuelType):
            return self.fuel.value
        return self.fuel

    @property
    def str_firstmot_or_used(self) -> str:
        if self.dt_firstmot is not None:
            return (
                f"This vehicle will be due its first MOT by *{self.dt_firstmot_year}/"
                f"{self.dt_firstmot_month:02d}/{self.dt_firstmot_day:02d}*"
            )
        return (
            f"This vehicle was first used on the road on *{self.dt_firstused_year}/"
            f"{self.dt_firstused_month:02d}/{self.dt_firstused_day:02d}*, and has *"
            f"{len(self.tests)}* logged test{'s' if len(self.tests) != 1 else ''}"
            " in its MOT history"
        )

    @property
    def str_recent_test(self) -> str:
        if len(self.tests) == 0:
            return ""
        return f"*Most recent MOT result*\n\n{self.tests[0].str}"
