from enum import Enum

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
            return f"<DVSAError {self.major}>"
        return f"<DVSAError {self.major}.{self.minor} [{self.reason} [{self.detail}]]>"


class MOTResult(Enum):
    Passed = "pass"
    Failed = "fail"


class DVSAVehicleType(Enum):
    HGV = "Heavy Goods Vehicle"
    PSV = "Passenger Service Vehicle"


class DVSATestType(Enum):
    aal = "Annual test"


class OdometerUnit(Enum):
    mi = "Mile"
    km = "Kilometer"
    NoUnit = "(zero)"


class MOTHistoryCommentType(Enum):
    User_Entered = "User-entered"
    Advisory = "Advisory note"
    Minor = "Minor (non-failing fault)"
    PRS = "PRS (pass after rectification at station)"
    Fail = "Failure"


class MOTHistoryComment:
    comment: str = None
    ctype: MOTHistoryCommentType = None

    def __init__(self, comment: dict):
        self.comment = comment["text"]
        self.ctype = coerce_type(comment["type"], MOTHistoryCommentType)
        if self.ctype is None:
            self.ctype = comment["type"]

    @property
    def str(self) -> str:
        return f"*{self.ctype.value if isinstance(self.ctype, MOTHistoryCommentType) else self.ctype}* - {self.comment}"

    @property
    def str_bullet(self) -> str:
        return f"- {self.str}"


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
        sep = self.dt_completed_date[4]
        (
            self.dt_completed_year,
            self.dt_completed_month,
            self.dt_completed_day,
        ) = self.dt_completed_date.split(sep)
        sep = self.dt_completed_time[2]
        (
            self.dt_completed_hour,
            self.dt_completed_minute,
            self.dt_completed_second,
        ) = self.dt_completed_time.split(sep)
        if entry.get("expiryDate", None) is not None:
            self.dt_expiry = entry["expiryDate"]
            sep = self.dt_expiry[4]
            (
                self.dt_expiry_year,
                self.dt_expiry_month,
                self.dt_expiry_day,
            ) = self.dt_expiry.split(sep)

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
        self.odometer_unit = coerce_type(entry.get("odometerUnit", "NoUnit"), OdometerUnit)
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
            f"{self.odometer_unit.value.lower()}{'s' if self.odometer_val > 1 else ''}*.\n\n"
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
        comments = "\n".join([comment.str_bullet for comment in self.comments])
        return (
            f"The following notes were included during the testing process:\n{comments}"
        )


class AnnualTest:
    performed_year: int
    performed_month: int
    performed_day: int
    test_type: DVSATestType
    result: MOTResult
    cert_num: str
    expiry_year: int
    expiry_month: int
    expiry_day: int
    defects: int
    advisories: int

    def __init__(self, testdata: dict):
        self.result = coerce_type(testdata["testResult"], MOTResult)
        self.test_type = coerce_type(testdata["testType"], DVSATestType)
        self.cert_num = testdata.get("testCertificateNumber", None)
        self.performed_year, self.performed_month, self.performed_day = testdata[
            "testDate"
        ].split(".")
        if self.cert_num is not None:
            self.expiry_year, self.expiry_month, self.expiry_day = testdata[
                "expiryDate"
            ].split(".")
        self.defects = coerce_type(testdata["numberOfDefectsAtTest"], int)
        self.advisories = coerce_type(testdata["numberOfAdvisoryDefectsAtTest"], int)


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
    resptmp: dict = None

    def __init__(self, bjss_response: dict):
        self.resptmp = bjss_response

        self.manufacturer = bjss_response.get("make", "Unknown").capitalize()
        self.model = bjss_response.get("model", "Unknown")
        if bjss_response.get("makeInFull", None) is not None:
            self.manufacturer, _, self.model = bjss_response.get("makeInFull", None).partition(" ")
        if self.manufacturer.upper() in acronym_mfrs:
            self.manufacturer = self.manufacturer.upper()
        elif self.manufacturer.lower() == "unknown":
            self.manufacturer = "[DVSA does not have the manufacturer on file]"
        else:
            self.manufacturer = self.manufacturer.capitalize()
        if self.model.lower() == "unknown":
            self.model = "[DVSA does not have the model on file]"
        else:
            self.model = self.model.capitalize()
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
            f"Vehicle with registration number *{self.number}* is a *{self.str_clryr}"
            f"{self.manufacturer} {self.model}*.\n\n"
            "*MOT history*\n"
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
        if self.dt_firstused is None and self.dt_firstmot is None:
            return (
                "This vehicle does not have any prior MOTs, and no date set for a first MOT, "
                "and may have been registered for regulatory testing purposes. "
            )
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
        return f"\n\n*Most recent MOT result*\n{self.tests[0].str}"


class DVSAVehicleAnnual:
    number: str
    manufacturer: str
    model: str
    type: DVSAVehicleType
    reg: str
    reg_year: int
    reg_month: int
    reg_day: int
    expiry: str
    expiry_year: int
    expiry_month: int
    expiry_day: int
    tests: list[AnnualTest]

    def __init__(self, historydata: dict):
        self.number = historydata["registration"]
        self.model = historydata.get("model", "Unknown")
        self.manufacturer = historydata.get("make", "Unknown")
        if self.manufacturer.upper() in acronym_mfrs:
            self.manufacturer = self.manufacturer.upper()
        elif self.manufacturer == "Unknown":
            self.manufacturer = "[DVSA does not have the manufacturer on file]"
        if self.model == "Unknown":
            self.model = "[DVSA does not have the model on file]"
        self.reg = historydata.get("registrationDate", None)
        self.expiry = historydata.get("expiryDate", None)
        self.type = coerce_type(historydata.get("vehicleType", None), DVSAVehicleType)
        self.tests = [AnnualTest(data) for data in historydata["annualTests"]]


class DVSAVehiclesAnnual:
    vehicles: list[DVSAVehicleAnnual]

    def __init__(self, response: dict):
        self.vehicles = [DVSAVehicleAnnual(data) for data in response]

