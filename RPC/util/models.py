from enum import Enum, auto

from RPC.util.coercion import coerce_type

# Hacky way of making manufacturer names less nasty
acronym_mfrs = (
    "A.S.A",
    "A.S.A.",
    "A.T.S",
    "A.T.S.",
    "AAD",
    "AC",
    "ACE EV",
    "ACE",
    "ACMA",
    "AEC",
    "AGA",
    "AGF",
    "AIL",
    "AIM",
    "AJS",
    "AJW",
    "AKT",
    "AM",
    "AMC",
    "AMZ",
    "API",
    "APIS",
    "ARO",
    "ASA",
    "ATS",
    "AVANI",
    "AWS",
    "AWZ",
    "BAC",
    "BAIC",
    "BAW",
    "BET",
    "BIOMAN",
    "BMC",
    "BMTF",
    "BMW",
    "BSA",
    "BYD",
    "CASAL",
    "CMC",
    "CNA",
    "CNHTC",
    "CT&T",
    "CTR",
    "CTT",
    "CWS",
    "CZ",
    "DAF",
    "DEVS",
    "DFM",
    "DIM",
    "DINA",
    "DKR",
    "DKW",
    "DMW",
    "DNA",
    "DOK-ING",
    "DOT",
    "DYL",
    "E-Z-GO",
    "ELVO",
    "EMW",
    "ENC",
    "ESO",
    "EVX",
    "EZ-GO",
    "EZGO",
    "F.L.A.G",
    "F.L.A.G.",
    "FAKA",
    "FAMEL",
    "FAP",
    "FAS",
    "FAW",
    "FB",
    "FCA",
    "FIAMC",
    "FLAG",
    "FN",
    "FNM",
    "FNSS",
    "FPV",
    "FSC",
    "FSM",
    "FSO",
    "FSR",
    "GAC",
    "GAZ",
    "GEM",
    "GKD",
    "GLM",
    "GM",
    "GMC",
    "GMSV",
    "GMZ",
    "GOVECS",
    "GTA",
    "HRD",
    "HTT",
    "IAME",
    "IAVA",
    "ICML",
    "IDA",
    "IKA",
    "IMT",
    "IMZ",
    "INKAS",
    "IWL",
    "JAC",
    "JAP",
    "JPX",
    "KAL",
    "KMZ",
    "KR",
    "KSU",
    "KTM",
    "KTX",
    "LAZ",
    "LIAZ",
    "LML",
    "LMX",
    "M.I.S.A.",
    "M.I.S.A",
    "MAC",
    "MAN SE",
    "MAN",
    "MAS",
    "MAVA",
    "MAZ",
    "MCI",
    "MDI",
    "MEBEA",
    "MG",
    "MISA",
    "MMZ",
    "MTT",
    "MTX",
    "MV",
    "MVM",
    "MZKT",
    "MZ",
    "NAG",
    "NATI",
    "NEVS",
    "NIU",
    "NSU",
    "O.M",
    "O.M.",
    "O.S.C.A",
    "O.S.C.A.",
    "OEC",
    "OK",
    "OM",
    "OSCA",
    "PAZ",
    "PGO",
    "PMZ",
    "RAESR",
    "RAF",
    "REO",
    "ROMAN",
    "RUSI",
    "S.C.A.T",
    "S.C.A.T.",
    "S.P.A",
    "S.P.A.",
    "SAIC",
    "SAIPA",
    "SAZ",
    "SCAT",
    "SCG",
    "SEAT",
    "SFM",
    "SHL",
    "SIAM",
    "SICRAF",
    "SIN",
    "SIS",
    "SM",
    "SMZ",
    "SNVI",
    "SPA",
    "SRT",
    "SSC",
    "SWM",
    "SYM",
    "TAC",
    "TAM",
    "TGB",
    "TH!NK",
    "TIZ",
    "TMC",
    "TMZ",
    "TN'G",
    "TNG",
    "TNT",
    "TOGG",
    "TVR",
    "TVS",
    "TWN",
    "UAZ",
    "UD",
    "UMM",
    "VAM",
    "VDL",
    "VLF",
    "VPG",
    "VUHL",
    "W",
    "WFM",
    "WSK",
    "Z",
    "ZAZ",
    "ZENN",
    "ZID",
    "ZSD",
    "ÖAF",
)

months = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


class EuroStatus(Enum):
    """
    European Emission Standards bands
    """

    EURO0 = auto()
    EUROI = auto()
    EUROII = auto()
    EUROIII = auto()
    EUROIV = auto()
    EUROV = auto()
    EUROVI = auto()
    EURO1 = auto()
    EURO2 = auto()
    EURO3 = auto()
    EURO4 = auto()
    EURO5 = auto()
    EURO5a = auto()
    EURO5b = auto()
    EURO6 = auto()
    EURO6b = auto()
    EURO6c = auto()
    EURO6d = auto()
    EURO6d_temp = auto()
    EURO7 = auto()


class FuelType(Enum):
    """
    Fuel types
    """

    Diesel = auto()
    Electricity = auto()
    Hybrid = "Hybrid Electric"
    Petrol = auto()
    Steam = auto()


class IVATypeApproval(Enum):
    """
    Individual Vehicle Approval types
    Not included are types C, R, S, and T (agricultural) or Non-road mobile machinery
    """

    L1e = "a low-powered moped or two-wheeled vehicle"
    L2e = "a low-powered three-wheeled vehicle"
    L3e = "a motorcycle"
    L4e = "a motorcycle with sidecar"
    L5e = "a motorised tricycle"
    L6e = "a low-powered four-wheeled vehicle or light quadricycle"
    L7e = "a heavy four-wheeled vehicle or quadricycle"
    M1 = "a passenger vehicle"
    M2 = "a bus or coach with at most 8 passenger seats and a maximum weight below or exactly 5t"
    M3 = "a bus or coach with at most 8 passenger seats and a maximum weight above 5t"
    N1 = "a light goods vehicle with maximum weight up to 3500kg"
    N2 = "a heavy goods vehicle with maximum weight between 3.5t and 12t"
    N3 = "a heavy goods vehicle with maximum weight above 12t"
    O1 = "a very light trailer with maximum weight below or exactly 0.75t"
    O2 = "a light trailer with maximum weight between 0.75t and 3.5t"
    O3 = "a medium trailer with maximum weight between 3.5t and 10t"
    O4 = "a heavy trailer with maximum weight above 10t"


class DVLAVehicle:
    number: str = None
    manufacturer: str = None
    colour: str = None
    year: int = None
    layout: str = None
    fuel: FuelType = None
    capacity: int = None
    emissions: int = None
    emissions_real: int = None
    euro: EuroStatus = None
    reg_month: int = None
    reg_year: int = None
    dvla_reg_month: int = None
    dvla_reg_year: int = None
    exportable: bool = None
    vfivec_day: int = None
    vfivec_month: int = None
    vfivec_year: int = None
    taxed: bool = None
    tax_due_day: int = None
    tax_due_month: int = None
    tax_due_year: int = None
    art_end_date: str = None
    moted: bool = None
    mot_until_day: int = None
    mot_until_month: int = None
    mot_until_year: int = None
    weight_rev: int = None
    autonomous: bool = None
    type_app: str = None

    def __init__(self, ves_response):
        self.number = ves_response["registrationNumber"].upper()
        self.manufacturer = ves_response["make"].capitalize()
        if self.manufacturer.upper() in acronym_mfrs:
            self.manufacturer = self.manufacturer.upper()
        self.colour = ves_response["colour"].lower()
        self.year = coerce_type(ves_response["yearOfManufacture"], int)

        self.layout = ves_response["wheelplan"].lower()

        self.fuel = coerce_type(ves_response["fuelType"], FuelType)
        self.capacity = coerce_type(ves_response["engineCapacity"], int)
        self.weight_rev = coerce_type(ves_response["revenueWeight"], int)
        self.autonomous = coerce_type(ves_response["automatedVehicle"], bool)

        self.emissions = coerce_type(ves_response["co2Emissions"], int)
        self.emissions_real = coerce_type(ves_response["realDrivingEmissions"], int)
        self.euro = coerce_type(ves_response["euroStatus"], EuroStatus)
        self.type_app = ves_response["typeApproval"].upper()

        self.reg_year = coerce_type(
            ves_response["monthOfFirstRegistration"].split("-")[0], int
        )
        self.reg_month = coerce_type(
            ves_response["monthOfFirstRegistration"].split("-")[1], int
        )
        self.dvla_reg = ves_response["monthOfFirstDvlaRegistration"]
        self.dvla_reg_year = coerce_type(
            ves_response["monthOfFirstDvlaRegistration"].split("-")[0], int
        )
        self.dvla_reg_month = coerce_type(
            ves_response["monthOfFirstDvlaRegistration"].split("-")[1], int
        )
        self.exportable = coerce_type(ves_response["markedForExport"], bool)

        self.vfivec = ves_response["dateOfLastV5CIssued"]
        self.vfivec_year = coerce_type(
            ves_response["dateOfLastV5CIssued"].split("-")[0], int
        )
        self.vfivec_month = coerce_type(
            ves_response["dateOfLastV5CIssued"].split("-")[1], int
        )
        self.vfivec_day = coerce_type(
            ves_response["dateOfLastV5CIssued"].split("-")[2], int
        )

        self.taxed = coerce_type(ves_response["taxStatus"], bool)
        self.tax_due_year = coerce_type(ves_response["taxDueDate"].split("-")[0], int)
        self.tax_due_month = coerce_type(ves_response["taxDueDate"].split("-")[1], int)
        self.tax_due_day = coerce_type(ves_response["taxDueDate"].split("-")[2], int)
        self.art_end_date = ves_response["artEndDate"]

        self.moted = coerce_type(ves_response["motStatus"], bool)
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
    def str_basic(self) -> str:
        return (
            f"Vehicle with registration number {self.number} is a {self.colour} {self.year} "
            f"{self.manufacturer}, whose wheel layout is {self.layout}. "
            f"It consumes {self.fuel.value}. "
            f"It was registered during the month of {self.reg_month},"
            f"{self.reg_year}{self.str_dvlareg}. "
            f"It is {'' if self.exportable else 'not '} marked for export. {self.str_euro}"
        )

    @property
    def str_dvlareg(self) -> str:
        if not self.dvla_reg:
            return ""
        return (
            f" (and was first registered to the DVLA during the month of {self.dvla_reg_month}"
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
            return ""
        return f"Vehicle has type application {self.type_app}"

    @property
    def str_emissions(self) -> str:
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
            f"{self.tax_due_year}/{self.tax_due_month}/{self.tax_due_day}"
            f"Additional tax rate "
            f"{'is not known' if self.art_end_date is None else 'ends on '+self.art_end_date}"
        )

    @property
    def str_mot(self) -> str:
        return (
            f"Vehicle MOT {'is valid until' if self.moted else 'expired on'} "
            f"{self.mot_until_year}/{self.mot_until_month}/{self.mot_until_day}."
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
