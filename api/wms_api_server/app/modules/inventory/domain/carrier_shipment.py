"""Match a complete physical carrier to an existing ST in exact base units."""
from fractions import Fraction
from .stock_quantity import convert_exact, quantity_text


def assert_matching_composition(physical_rows, document_rows):
    if not 1 <= len(physical_rows) <= 200 or not 1 <= len(document_rows) <= 200:
        raise ValueError("Carrier/ST composition is empty or exceeds the supported bound")
    physical, planned = {}, {}
    for article, base, quantity in physical_rows:
        if not article or not base:
            raise ValueError("Physical carrier SKU/base unit required")
        key = (article, base)
        physical[key] = physical.get(key, Fraction(0)) + Fraction(quantity_text(quantity))
    for article, quantity, base, numerator, denominator, scale in document_rows:
        if not article or not base or numerator is None or denominator is None or scale is None:
            raise ValueError("ST line requires an explicit unit conversion policy")
        if any(value != int(value) for value in (numerator, denominator, scale)):
            raise ValueError('Conversion policy requires integer factors and scale')
        converted = convert_exact(quantity, int(numerator), int(denominator), int(scale))
        key = (article, base)
        planned[key] = planned.get(key, Fraction(0)) + Fraction(converted)
    if physical != planned:
        raise ValueError("ST content differs from the complete physical carrier; correct the shipment layout")
