# Qwen: NI07.1 UI550
Prepared only; do not run additional model qualification automatically.
Review TransportNormPublisher, TransportNormHistory, TransportTariffSources and api.ts. Use isolated metadata and current authorized actor. Do not recreate ctx532, reset retired publisher535 or publish a tariff for an original carrier.
Cases: unknown response after commit -> saved identical OP/body retry returns one native version; confirmed409 -> refresh current source/head before editable new intent;403/network/500 do not allow dropping intent; separate exact actor/API/warehouse/source keys; malformed storage blocked; no password persisted. A successful publish followed by failed read must remain visibly published, not unknown.
History limit30, descending version keyset, stale response after switching source ignored. Current source fields versus frozen snapshot displayed distinctly; no PRICE/P/H or monetary costs effect. Record observed result, do not mark full NI07.1 accepted.
