from .oracle_gateway import OracleGateway
from .modules.resources.public import ScopedCaseReads, CaseReadPort


def scoped_case_reads() -> CaseReadPort:
    return ScopedCaseReads(OracleGateway())
