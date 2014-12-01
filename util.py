"""

    AppEngine has no support for locale
    string.format() doesn not support formatting number with dots as thousand separators
    But we need to format numbers.
    This is our aproach.

    @author    Markus Tacker <m@click4life.hiv>
    @copyright 2014 TLD dotHIV Registry GmbH | https://tld.hiv/

"""

class Format(object):
    LOCALE_DE = 'de'
    LOCALE_ES = 'es'
    LOCALE_FR = 'fr'
    LOCALE_PL = 'pl'
    LOCALE_EN = 'en'
    DEFAULT_LOCALE = 'en'

    def __init__(self, locale=None):
        self.locale = locale if locale else Format.DEFAULT_LOCALE

    def decimal(self, number):
        """
        Formats a decimal number.
        """
        number = int(number)
        if self.isDe():
            return "{:,}".format(number).replace(',', '.')
        return "{:,}".format(number)

    def money(self, number, ratio=1.0):
        """
        Formats a money value.
        """
        number = float(number) * ratio
        if self.isDe():
            if number < 0.01: # Cent
                pre, post = "{0:.1f} ct".format(number * 100).split('.')
            elif number < 1.0: # Decimal Cent
                return "{0:n} ct".format(number * 100)
            else:
                pre, post = "{0:,.2f} &euro;".format(number).split('.')
            pre = pre.replace(',', '.')
            return ','.join((pre, post))
        if number < 0.01: # Cent
            return "&euro;{0:.1f}&cent;".format(number * 100)
        elif number < 1.0: # Decimal Cent
            return "&euro;{0:n}&cent;".format(number * 100)
        return "&euro;{0:,.2f}".format(number)

    def decimalMoney(self, number, ratio=1.0):
        """
        Formats a money value as decimal.
        """
        decimal = self.decimal(float(number) * ratio)
        if self.isDe():
            return "%s &euro;" % decimal
        return "&euro;%s" % decimal

    def float(self, number):
        """
        Formats a float number.
        """
        if self.isDe():
            return ','.join(("%.1f" % float(number)).split('.'))
        return "%.1f" % float(number)

    def isDe(self):
        return self.locale in [Format.LOCALE_DE, Format.LOCALE_ES, Format.LOCALE_FR, Format.LOCALE_PL]
