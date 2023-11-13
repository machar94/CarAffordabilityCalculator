from dataclasses import dataclass
from enum import Enum


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


@dataclass
class Cost():
    '''
    Monthly costs
    '''
    fuel: float
    loan_payment: float
    maintenance: float
    total: float


@dataclass
class Car():
    make: str
    cost: float
    mpg: float
    cost: Cost
    # Vehicle ID on FeulEconomy.gov
    fe_id: int


@dataclass
class Loan():
    '''
    Loan characteristics
    '''
    term_length: int
    down_payment: float
    interest_rate: float


@dataclass
class User():
    weekly_miles: int
    credit_score: CreditScore


def loan_payment(loan: Loan, car: Car, costs: Cost):
    """
    Calculate monthly loan payment
    """
    
    loan_amount = max(car.cost - loan.down_payment, 0)
    total_interest = (loan.interest_rate / 12) * loan_amount * loan.term_length
    total_payments = total_interest + loan_amount
    costs.loan_payment = total_payments / loan.term_length

