from dataclasses import dataclass, field
from enum import Enum
import requests


############
# Defaults #
############

DEFAULT_CAR_ID = 46973
DEFAULT_CAR_PRICE = 30000
DEFAULT_WEEKLY_MILES = 192
DEFAULT_GAS_PRICE = 3.365
DEFAULT_DOWN_PAYMENT = 0.00
DEFAULT_TERM_LENGTH = 60

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
            return cls.SuperPrime
        elif selection == 2:
            return cls.NearPrime
        elif selection == 3:
            return cls.Prime
        elif selection == 4:
            return cls.SubPrime
        elif selection == 5:
            return cls.DeepSubPrime
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
    # Vehicle ID on FeulEconomy.gov
    fe_id: int = field(init=False)


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


def loan_payment(loan: Loan, car: Car, costs: Cost):
    """
    Calculate monthly loan payment
    """

    loan_amount = max(car.cost - loan.down_payment, 0)
    total_interest = (loan.interest_rate / 12) * loan_amount * loan.term_length
    total_payments = total_interest + loan_amount
    costs.loan_payment = total_payments / loan.term_length


def get_car_info(car_id: int) -> (str, float):
    """
    Get car information from FuelEconomy.gov API

    Returns:
        make: str
        mpg: float
    """
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
        print(e)

        return None, None

    return make, mpg


def calculate_gas_cost(car: Car, user: User):
    """
    Calculate monthly gas cost
    """

    car.monthly_cost.fuel = (user.weekly_miles / car.mpg) * user.gas_price * 4


def get_interest_rate():
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


def calculate_costs(cars: list, user: User, loan: Loan):
    """
    Calculate monthly costs for each car
    """

    for car in cars:
        loan_payment(loan, car, costs)
        calculate_gas_cost(car, user)
        car.monthly_cost.total = car.monthly_cost.fuel + \
            car.monthly_cost.loan_payment + car.monthly_cost.maintenance


########
# Main #
########


car_1 = Car()
car_1.fe_id = int(input("Enter car ID 1 (default: 46973): ") or DEFAULT_CAR_ID)
car_1.price = float(
    input("Enter car price 1 (default: $30,000): ") or DEFAULT_CAR_PRICE)

make, mpg = get_car_info(car_1.fe_id)
car_1.make = make
car_1.mpg = mpg

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


calculate_gas_cost(car_1, user_data)


print(user_data)
print(car_1)

calculate_costs([car_1], user_data, loan)
