#!/usr/bin/env python
"""

    Tests for util.

    @author    Markus Tacker <m@dotHIV.org>
    @copyright 2014 dotHIV e.V. | http://dotHIV.org

"""
import unittest
import util


class TestCase(unittest.TestCase):
    def test_decimal(self):
        self.assertEquals('500.000', util.Format('de').decimal(500000))
        self.assertEquals('500.000', util.Format('de').decimal('500000'))
        self.assertEquals('500,000', util.Format('en').decimal(500000))
        self.assertEquals('500,000', util.Format('en').decimal('500000'))
        self.assertEquals('500,000', util.Format().decimal(500000))
        self.assertEquals('500,000', util.Format().decimal(500000))
        self.assertEquals('500,000', util.Format().decimal('500000'))

    def test_float(self):
        self.assertEquals('0,1', util.Format('de').float(1.0/10))
        self.assertEquals('0.1', util.Format('en').float(1.0/10.))
        self.assertEquals('0.1', util.Format().float(1.0/10))

    def test_decimal_money(self):
        self.assertEquals('500.000 &euro;', util.Format('de').decimalMoney(500000))
        self.assertEquals('500.000 &euro;', util.Format('de').decimalMoney('500000'))
        self.assertEquals('$500,000', util.Format('en').decimalMoney(500000))
        self.assertEquals('$500,000', util.Format('en').decimalMoney('500000'))
        self.assertEquals('$500,000', util.Format().decimalMoney(500000))
        self.assertEquals('$500,000', util.Format().decimalMoney('500000'))

    def test_money(self):
        self.assertEquals('500.000,00 &euro;', util.Format('de').money(500000))
        self.assertEquals('500.000,00 &euro;', util.Format('de').money('500000'))
        self.assertEquals('$500,000.00', util.Format('en').money(500000))
        self.assertEquals('$500,000.00', util.Format('en').money('500000'))
        self.assertEquals('$500,000.00', util.Format().money(500000))
        self.assertEquals('$500,000.00', util.Format().money('500000'))
        self.assertEquals('0,1 ct', util.Format('de').money(0.001))
        self.assertEquals('0.1&cent;', util.Format('en').money(0.001))
        self.assertEquals('0.1&cent;', util.Format().money(0.001))

if __name__ == '__main__':
    unittest.main()
