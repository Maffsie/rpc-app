from enum import Enum, auto

from requests import Response

from RPC.util.coercion import coerce_type

from .dvla import FuelType, acronym_mfrs, months


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
                    "Unable to look up registration number due to an API error. The DVLA responded "
                    "Forbidden, which is not a temporary problem. Please contact @Maffsie."
                )
                return
            case 404:
                self.reason = (
                    "Registration number is in a valid format, but was not recognised by the DVLA. "
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
    Passed = auto()
    Failed = auto()


class OdometerUnit(Enum):
    mi = "Miles"
    km = "Kilometers"


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
    def str(self):
        return f"{self.ctype.value} - {self.comment}"


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
        self.comments = [
            MOTHistoryComment(comment) for comment in entry["rfrAndComments"]
        ]


class DVSAVehicle:
    number: str = None
    manufacturer: str = None
    model: str = None
    colour: str = None
    fuel: FuelType = None
    dt_firstused: str = None
    dt_firstused_year: int = None
    dt_firstused_month: int = None
    dt_firstused_day: int = None
    dt_firstmot: str = None
    dt_firstmot_year: int = None
    dt_firstmot_month: int = None
    dt_firstmot_day: int = None

    def __init__(self, bjss_response):
        self.number = bjss_response["registrationNumber"].upper()
        self.manufacturer = bjss_response["make"].capitalize()
        if self.manufacturer.upper() in acronym_mfrs:
            self.manufacturer = self.manufacturer.upper()
        self.colour = ves_response["colour"].lower()
        self.year = coerce_type(ves_response["yearOfManufacture"], int)

        self.layout = ves_response["wheelplan"].lower()

        self.fuel = coerce_type(ves_response.get("fuelType", None), FuelType)
        self.capacity = coerce_type(ves_response.get("engineCapacity", None), int)
        self.weight_rev = coerce_type(ves_response.get("revenueWeight", None), int)
        self.autonomous = coerce_type(ves_response.get("automatedVehicle", None), bool)

        self.emissions = coerce_type(ves_response.get("co2Emissions", None), int)
        self.emissions_real = coerce_type(
            ves_response.get("realDrivingEmissions", None), int
        )
        self.euro = coerce_type(ves_response.get("euroStatus", None), EuroStatus)
        self.type_app = ves_response.get("typeApproval", "").upper()
        self.type_app_d = coerce_type(self.type_app, IVATypeApproval)

        if ves_response.get("monthOfFirstRegistration", None) is not None:
            self.reg_year = coerce_type(
                ves_response["monthOfFirstRegistration"].split("-")[0], int
            )
            self.reg_month = coerce_type(
                ves_response["monthOfFirstRegistration"].split("-")[1], int
            )
        self.dvla_reg = ves_response.get("monthOfFirstDvlaRegistration", None)
        if self.dvla_reg is not None:
            self.dvla_reg_year = coerce_type(
                ves_response["monthOfFirstDvlaRegistration"].split("-")[0], int
            )
            self.dvla_reg_month = coerce_type(
                ves_response["monthOfFirstDvlaRegistration"].split("-")[1], int
            )
        self.exportable = coerce_type(ves_response.get("markedForExport", None), bool)

        self.vfivec = ves_response.get("dateOfLastV5CIssued", None)
        if self.vfivec is not None:
            self.vfivec_year = coerce_type(
                ves_response["dateOfLastV5CIssued"].split("-")[0], int
            )
            self.vfivec_month = coerce_type(
                ves_response["dateOfLastV5CIssued"].split("-")[1], int
            )
            self.vfivec_day = coerce_type(
                ves_response["dateOfLastV5CIssued"].split("-")[2], int
            )

        self.taxed = coerce_type(ves_response.get("taxStatus", None), bool)
        if self.taxed is not None and ves_response.get("taxDueDate", None) is not None:
            self.tax_due_year = coerce_type(
                ves_response["taxDueDate"].split("-")[0], int
            )
            self.tax_due_month = coerce_type(
                ves_response["taxDueDate"].split("-")[1], int
            )
            self.tax_due_day = coerce_type(
                ves_response["taxDueDate"].split("-")[2], int
            )
        self.art_end_date = ves_response.get("artEndDate", None)

        self.moted = coerce_type(ves_response.get("motStatus", None), bool)
        if (
            self.moted is not None
            and ves_response.get("motExpiryDate", None) is not None
        ):
            self.mot_until_year = coerce_type(
                ves_response["motExpiryDate"].split("-")[0], int
            )
            self.mot_until_month = coerce_type(
                ves_response["motExpiryDate"].split("-")[1], int
            )
            self.mot_until_day = coerce_type(
                ves_response["motExpiryDate"].split("-")[2], int
            )

    @property
    def str_full(self) -> str:
        return (
            "*Basic information*\n"
            f"Vehicle with registration number *{self.number}* is a *{self.colour} {self.year} "
            f"{self.manufacturer}*, whose wheel layout is *{self.layout}*.\n"
            f"It has {self.str_fuel} engine, and was registered during the month of "
            f"{months[self.reg_month]}, {self.reg_year}{self.str_dvlareg}. "
            f"It is {'' if self.exportable else 'not '}marked for export. {self.str_type}\n\n"
            "*Tax and MOT*\n"
            f"{self.str_tax}\n{self.str_mot}\n{self.str_vfivec}\n\n"
            "*Emissions & classification*\n"
            f"{self.str_euro_and_emissions}."
        )

    @property
    def str_basic(self) -> str:
        return (
            f"Vehicle with registration number {self.number} is a {self.colour} {self.year} "
            f"{self.manufacturer}, whose wheel layout is {self.layout}. "
            f"It consumes {self.fuel.name}. "
            f"It was registered during the month of {months[self.reg_month]}, "
            f"{self.reg_year}{self.str_dvlareg}. "
            f"It is {'' if self.exportable else 'not '}marked for export. {self.str_euro}"
        )

    @property
    def str_fuel(self) -> str:
        if isinstance(self.fuel, FuelType):
            return self.fuel.value
        return self.fuel

    @property
    def str_dvlareg(self) -> str:
        if not self.dvla_reg:
            return ""
        return (
            f" (and was first registered to the DVLA during the month of {months[self.dvla_reg_month]}"
            f", {self.dvla_reg_year})"
        )

    @property
    def str_euro(self) -> str:
        if not self.euro:
            return (
                "The emissions of this vehicle have not been classified under the European "
                "Emission Standards band rating, or its classification is not known to the DVLA"
            )
        return f"The emissions of this vehicle fall under the {self.euro.value} band."

    @property
    def str_type(self) -> str:
        if not self.type_app:
            return "Vehicle has no registered type approval."
        return f"Vehicle has type approval {self.type_app}, which defines it as {self.type_app_d.value.lower()}."

    @property
    def str_euro_and_emissions(self) -> str:
        if (
            not self.emissions
            and not self.capacity
            and not self.emissions_real
            and not self.euro
        ):
            return (
                "The DVLA has no records or recorded European Emissions Standard band rating"
                "for this vehicle."
            )
        if self.capacity and not self.emissions and not self.emissions_real:
            return f"{self.str_emissions_capacity}. {self.str_euro}"
        return f"{self.str_emissions} {self.str_euro}"

    @property
    def str_emissions(self) -> str:
        if not self.emissions and not self.capacity and not self.emissions_real:
            return "The DVLA has no records about the vehicle's engine capacity or emissions."
        return f"{self.str_emissions_capacity}, {self.str_emissions_co}. {self.str_emissions_real}"

    @property
    def str_emissions_capacity(self) -> str:
        if not self.capacity:
            return "Vehicle doesn't have an engine, or its engine capacity is not known to the DVLA"
        return f"Vehicle has an engine capacity of {self.capacity} cubic centimetres"

    @property
    def str_emissions_co(self) -> str:
        if not self.emissions:
            return "and produces no emissions, or the DVLA is not aware of its emissions rating"
        return (
            f"and produces emissions of {self.emissions}g of carbon dioxide (CO2) per "
            f"kilometre driven"
        )

    @property
    def str_emissions_real(self) -> str:
        if not self.emissions_real:
            return (
                "Its real driving emissions, if different, are not known to the DVLA."
            )
        return f"It has real driving emissions of {self.emissions_real} grams per kilometre."

    @property
    def str_tax(self) -> str:
        if self.taxed == "SORN":
            return (
                "Vehicle is registered for off-road use only, or is otherwise not able to use "
                "normal roads, and has a SORN (Statutory off-road notice) registered against it."
            )
        return (
            f"Vehicle is {'not ' if not self.taxed else ''}currently taxed. "
            f"Tax expire{'s' if self.taxed else 'd'} on "
            f"{self.tax_due_year}/{self.tax_due_month}/{self.tax_due_day}."
            f"{'' if self.art_end_date is None else 'Additional tax rate ends on '+self.art_end_date}"
        )

    @property
    def str_mot(self) -> str:
        return (
            f"Vehicle MOT {'is valid until' if self.moted else 'expired on'} "
            f"{self.mot_until_year}/{self.mot_until_month}/{self.mot_until_day}.\n"
            f"In-depth MOT information [may be available online](https://www.check-mot.service.gov.uk/results?registration={self.number})"
        )

    @property
    def str_vfivec(self) -> str:
        if not self.vfivec:
            return (
                "Vehicle does not have a logbook (V5C) or it is not known to the DVLA."
            )
        return (
            f"Vehicle logbook (V5C) was last issued "
            f"{self.vfivec_year}/{self.vfivec_month}/{self.vfivec_day}."
        )
