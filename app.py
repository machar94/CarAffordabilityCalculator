from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

import requests
import csv
import pprint

############
# Defaults #
############

DEFAULT_CAR_ID = 46973
DEFAULT_CAR_PRICE = 30000
DEFAULT_WEEKLY_MILES = 192
DEFAULT_GAS_PRICE = 3.365
DEFAULT_DOWN_PAYMENT = 0.00
DEFAULT_TERM_LENGTH = 60

DEFAULT_DB_PATH = "data/maintenance.csv"

###############
# Dataclasses #
###############


class CreditScore(Enum):
    DeepSubPrime = 13.42
    SubPrime = 10.79
    NearPrime = 8.12
    Prime = 5.82
    SuperPrime = 4.75

    def __str__(self):
        if self is CreditScore.DeepSubPrime:
            return "300-500"
        elif self is CreditScore.SubPrime:
            return "501-600"
        elif self is CreditScore.NearPrime:
            return "601-660"
        elif self is CreditScore.Prime:
            return "661-780"
        elif self is CreditScore.SuperPrime:
            return "781-850"

    @classmethod
    def from_int(cls, selection):
        if selection == 1:
            return cls.DeepSubPrime
        elif selection == 2:
            return cls.SubPrime
        elif selection == 3:
            return cls.NearPrime
        elif selection == 4:
            return cls.Prime
        elif selection == 5:
            return cls.SuperPrime
        else:
            raise ValueError("Invalid selection")


@dataclass
class Cost():
    '''
    Monthly costs
    '''
    fuel: float = field(init=False, default=None)
    loan_payment: float = field(init=False, default=None)
    maintenance: float = field(init=False, default=None)
    total: float = field(init=False, default=None)


@dataclass
class Car():
    make: str = field(init=False)
    price: float = field(init=False)
    mpg: float = field(init=False)
    monthly_cost: Cost = field(init=False, default_factory=Cost)


@dataclass
class Loan():
    '''
    Loan characteristics
    '''
    down_payment: float = field(init=False)
    interest_rate: float = field(init=False)
    term_length: int = field(init=False)


@dataclass
class User():
    gas_price: float = field(init=False)
    weekly_miles: int = field(init=False)


@dataclass
class AutoMaintenance():
    cost_1_to_60: float
    cost_61_to_120: float


#############
# Functions #
#############


def read_maintenance_costs() -> Dict[str, AutoMaintenance]:
    """
    Read local maintenance database
    """

    reader = csv.reader(open(DEFAULT_DB_PATH, "r"))

    next(reader)  # Skip header

    maintenance_costs = {}

    for row in reader:
        make = row[0].upper()
        cost_1_to_60 = float(row[1])
        cost_61_to_120 = float(row[2])

        maintenance_costs[make] = AutoMaintenance(cost_1_to_60, cost_61_to_120)

    return maintenance_costs


def get_car_info(makes: List[str]) -> (str, float):
    """
    Get car information from FuelEconomy.gov API

    Args:
        makes: List of valid makes
    Returns:
        make: str 
        mpg: float
    """

    while (True):
        car_id = input("Enter car ID (default: 46973): ") or DEFAULT_CAR_ID
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/{car_id}"
        headers = {
            "User-Agent": "CarLoanCalculator/1.0",
            "Accept": "application/json"
        }

        try:
            response = requests.get(url, headers=headers)
            response_json = response.json()

            make = response_json["make"]
            mpg = float(response_json["comb08"])

        except requests.exceptions.RequestException as e:
            print("Error requesting vehicle information for ID: ", car_id)
            print("Please try again.")
            print(e)
            continue

        if make.upper() not in makes:
            print(
                f"No maintenance data available for {make}. Please select another vehicle.")
            continue

        return make.upper(), mpg


def get_interest_rate() -> float:
    """
    Convert credit score from user to interest rate
    """

    for i, score in enumerate(CreditScore, start=1):
        print(i, ". ", score)

    while (True):
        selection = input("Enter credit score (1-5): ")

        try:
            credit_score = CreditScore.from_int(int(selection))
        except ValueError as e:
            print("Invalid selection. Please try again.")
            continue
        else:
            break

    return credit_score.value


def monthly_loan_payment(car: Car, loan: Loan) -> float:
    """
    Calculate monthly loan payment
    """

    loan_amount = max(car.price - loan.down_payment, 0)
    total_interest = (loan.interest_rate / 100 / 12) * \
        loan_amount * loan.term_length
    total_payments = total_interest + loan_amount
    loan_payment = total_payments / loan.term_length

    # Round loan_payment to 2 decimal places
    return round(loan_payment, 2)


def monthly_gas_cost(car: Car, user: User) -> float:
    """
    Calculate monthly gas cost
    """

    gas_cost = (user.weekly_miles / car.mpg) * user.gas_price * 4
    return round(gas_cost, 2)


def monthly_maintenance_cost(car: Car, loan: Loan, maintenance_costs: Dict[str, AutoMaintenance]) -> float:
    """
    Calculate monthly maintenance cost
    """

    cost_1_to_60 = maintenance_costs[car.make].cost_1_to_60
    cost_61_to_120 = maintenance_costs[car.make].cost_61_to_120

    cost_before_5_years = min(60, loan.term_length) * cost_1_to_60 / 60
    cost_after_5_years = max(0, loan.term_length - 60) * cost_61_to_120 / 60

    avg_monthly_maintenance_cost = (
        cost_after_5_years + cost_before_5_years) / loan.term_length
    return round(avg_monthly_maintenance_cost, 2)


def calculate_costs(cars: list, user: User, loan: Loan):
    """
    Calculate monthly costs for each car
    """

    for car in cars:
        car.monthly_cost.fuel = monthly_gas_cost(car, user)
        car.monthly_cost.loan_payment = monthly_loan_payment(car, loan)
        car.monthly_cost.maintenance = monthly_maintenance_cost(
            car, loan, maintenance_costs)

        car.monthly_cost.total = car.monthly_cost.fuel + \
            car.monthly_cost.loan_payment + car.monthly_cost.maintenance


########
# Main #
########

pp = pprint.PrettyPrinter(indent=4)

print("Welcome to the Car Loan Calculator!")

maintenance_costs = read_maintenance_costs()
make, mpg = get_car_info(list(maintenance_costs.keys()))

car_1 = Car()
car_1.make = make
car_1.mpg = mpg
car_1.price = float(
    input("Enter car price 1 (default: $30,000): ") or DEFAULT_CAR_PRICE)

user_data = User()
user_data.weekly_miles = float(
    input("Enter weekly miles (default: 192): ") or DEFAULT_WEEKLY_MILES)
user_data.gas_price = float(
    input("Enter gas price (default: $3.365): ") or DEFAULT_GAS_PRICE)

loan = Loan()
loan.down_payment = float(
    input("Enter down payment (default: $0.00): ") or DEFAULT_DOWN_PAYMENT)
loan.term_length = int(
    input("Enter loan term in months (default: 60): ") or DEFAULT_TERM_LENGTH)
loan.interest_rate = get_interest_rate()

calculate_costs([car_1], user_data, loan)
print(user_data)
print(car_1)
