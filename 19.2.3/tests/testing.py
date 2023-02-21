import pytest
from app.calculator import Calculator

class TestCalc:
    def setup(self):
        self.calc = Calculator

    def test_multiply_calculate_correctly(self):
        assert self.calc.multiply(self, 3, 3) == 9

    def test_division_calculate_correctly(self):
        assert self.calc.division(self, 9, 3) == 3

    def test_subtraction_calculate_correctly(self):
        assert self.calc.subtraction(self, 10, 3) == 7

    def test_adding_calculate_correctly(self):
        assert self.calc.adding(self, 10, 5) == 15

    def test_zero_division(self):
        with pytest.raises(ZeroDivisionError):
            self.calc.division(self, 2, 0)

    def teardown(self):
        print("Выполнение Teardown")