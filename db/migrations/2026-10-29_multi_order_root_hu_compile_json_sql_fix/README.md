# Multi-order shipment compile JSON SQL fix

The compiler copies JSON fields into PL/SQL scalars before using them in SQL predicates. Oracle rejects JSON object method calls inside SQL predicates.
