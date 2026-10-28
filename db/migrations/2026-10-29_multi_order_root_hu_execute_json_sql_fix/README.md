# Multi-order root-HU execution JSON SQL fix

The execution branch copies JSON values to PL/SQL variables before SQL predicates. This keeps the compiler and execution paths compatible with Oracle JSON SQL restrictions.
