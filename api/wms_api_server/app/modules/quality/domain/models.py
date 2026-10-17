"""Immutable read models supplied by native HU/capture owners, not new stock entities.
Producer references are provenance declarations, not cryptographic attestations.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
import re
from typing import Literal


class HuMassError(ValueError):
    pass


def identity(value: str) -> None:
    if not isinstance(value,str) or not 1<=len(value)<=200 or value.strip()!=value:
        raise HuMassError('HU_MASS_IDENTIFIER_REQUIRED')


def aware(value: datetime) -> None:
    if not isinstance(value,datetime) or value.utcoffset() is None:
        raise HuMassError('HU_MASS_AWARE_TIME_REQUIRED')
    roundtrip=value.astimezone(timezone.utc).astimezone(value.tzinfo)
    if value.replace(tzinfo=None)!=roundtrip.replace(tzinfo=None)or value.utcoffset()!=roundtrip.utcoffset():
        raise HuMassError('HU_MASS_NONEXISTENT_LOCAL_TIME')


def utc_instant(value: datetime) -> datetime:
    aware(value)
    return value.astimezone(timezone.utc)


def mass(value: Decimal) -> None:
    if not isinstance(value,Decimal) or not value.is_finite() or value<0:
        raise HuMassError('HU_MASS_FINITE_NONNEGATIVE_DECIMAL_REQUIRED')
    digits=value.as_tuple()
    if max(0,-digits.exponent)>9 or len(digits.digits)+max(0,digits.exponent)>18:
        raise HuMassError('HU_MASS_SOURCE_PRECISION_18_9_REQUIRED')


@dataclass(frozen=True)
class CompositionIdentity:
    """Opaque native identity. This module does not invent/recompute the HU hash."""
    identifier: str
    content_version: int
    signature_domain: str
    signature_version: int
    composition_signature: str

    def __post_init__(self) -> None:
        identity(self.identifier)
        identity(self.signature_domain)
        if type(self.content_version)is not int or self.content_version<0 or type(self.signature_version)is not int or self.signature_version<1:
            raise HuMassError('HU_MASS_NATIVE_VERSION_REQUIRED')
        if not isinstance(self.composition_signature,str) or not re.fullmatch('[A-F0-9]{64}',self.composition_signature):
            raise HuMassError('HU_MASS_NATIVE_SIGNATURE_REQUIRED')


@dataclass(frozen=True)
class MassEvidence:
    """Existing archive/policy projection. Never an equipment capture wire packet."""
    binding: CompositionIdentity
    basis: Literal['GROSS','TARE']
    unit: Literal['KG']
    weight_kg: Decimal
    source: Literal['MEASURED','ESTIMATED']
    source_domain: str
    source_version: int
    reference: str
    producer_proof: str
    effective_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.binding,CompositionIdentity):raise HuMassError('HU_MASS_NATIVE_BINDING_REQUIRED')
        mass(self.weight_kg)
        for value in (self.source_domain,self.reference,self.producer_proof):identity(value)
        aware(self.effective_at);aware(self.expires_at)
        if self.basis not in ('GROSS','TARE')or self.unit!='KG' or self.source not in ('MEASURED','ESTIMATED'):
            raise HuMassError('HU_MASS_EXPLICIT_BASIS_UNIT_SOURCE_REQUIRED')
        if type(self.source_version)is not int or self.source_version<1 or utc_instant(self.expires_at)<=utc_instant(self.effective_at):
            raise HuMassError('HU_MASS_EVIDENCE_VERSION_WINDOW_REQUIRED')


@dataclass(frozen=True)
class HuMassNode:
    binding: CompositionIdentity
    warehouse_id: int
    cell: str
    direct_children: tuple[str,...]
    leaf_stock_keys: tuple[str,...]
    own_tare: MassEvidence | None = None
    observed_gross: MassEvidence | None = None
    estimated_gross: MassEvidence | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.binding,CompositionIdentity):raise HuMassError('HU_MASS_NATIVE_BINDING_REQUIRED')
        identity(self.cell)
        if type(self.warehouse_id)is not int or self.warehouse_id<1:
            raise HuMassError('HU_MASS_PHYSICAL_WAREHOUSE_REQUIRED')
        if type(self.direct_children)is not tuple or type(self.leaf_stock_keys)is not tuple:
            raise HuMassError('HU_MASS_IMMUTABLE_CLOSURE_REQUIRED')
        if len(self.direct_children)>200 or len(self.leaf_stock_keys)>10000:
            raise HuMassError('HU_MASS_NODE_COLLECTION_BOUND')
        for value in (*self.direct_children,*self.leaf_stock_keys):identity(value)
        if self.direct_children and self.leaf_stock_keys:
            raise HuMassError('HU_MASS_CONTAINER_CANNOT_DUPLICATE_LEAF_STOCK')
        if any(value is not None and not isinstance(value,MassEvidence)for value in (self.own_tare,self.observed_gross,self.estimated_gross)):
            raise HuMassError('HU_MASS_TYPED_EVIDENCE_REQUIRED')
        if self.observed_gross is not None and self.observed_gross.source!='MEASURED':
            raise HuMassError('HU_MASS_OBSERVED_REQUIRES_MEASURED_SOURCE')
        if self.estimated_gross is not None and self.estimated_gross.source!='ESTIMATED':
            raise HuMassError('HU_MASS_ESTIMATE_SOURCE_REQUIRED')


@dataclass(frozen=True)
class FrozenHuMassInput:
    root: CompositionIdentity
    nodes: tuple[HuMassNode,...]
    producer_proof: str
    frozen_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.root,CompositionIdentity):raise HuMassError('HU_MASS_NATIVE_BINDING_REQUIRED')
        identity(self.producer_proof);aware(self.frozen_at);aware(self.expires_at)
        if type(self.nodes)is not tuple or not 1<=len(self.nodes)<=200:
            raise HuMassError('HU_MASS_CLOSURE_BOUND_200')
        if not all(isinstance(node,HuMassNode)for node in self.nodes):raise HuMassError('HU_MASS_NATIVE_NODES_REQUIRED')
        if utc_instant(self.expires_at)<=utc_instant(self.frozen_at):
            raise HuMassError('HU_MASS_FREEZE_WINDOW_REQUIRED')


@dataclass(frozen=True)
class NodeMassProjection:
    identifier: str
    expected_gross_kg: Decimal | None
    expected_source: Literal['CALCULATED_MEASURED_INPUTS','CALCULATED_WITH_ESTIMATES','ESTIMATED','UNKNOWN']
    observed_gross: MassEvidence | None
    observed_state: str
    difference_kg: Decimal | None
    reasons: tuple[str,...]


@dataclass(frozen=True)
class HuMassProjection:
    root_identifier: str
    freeze_state: Literal['CURRENT','STALE','EXPIRED','FUTURE']
    as_of: datetime
    nodes: tuple[NodeMassProjection,...]
    projection_sha256: str
    producer_proof_verified: Literal[False] = field(default=False,init=False)
    quality_release_approved: Literal[False] = field(default=False,init=False)
