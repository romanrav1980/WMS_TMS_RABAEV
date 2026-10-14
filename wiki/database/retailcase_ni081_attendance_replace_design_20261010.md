# NI08.1 / NS33 — атомарная корректировка планового выхода,150

Resources owns original RRL_WORKLOAD_ATTENDANCE and cancellation facts. Extend existing RRL_WORKLOAD_CONFIG_API with REPLACE_ATTENDANCE; same operation/actor/body identity, same original scoped actor, same store_attendance qualification/overlap/aware interval rule.

One metadata CONFIG fence, source cancellation plus new immutable plan plus operation result in caller UOW. Source plan ID is optimistic immutable version; already-cancelled source refuses concurrent different replacement. Result records replaced source ID and new plan ID. No rewrite of actual shift/session/task/presence or stock.

Native savepoint after metadata fence covers all actions: outer PL/SQL catch+commit must not leave operation placeholder/cancellation without new plan. Recheck actor after fence and before replay. Replacement new interval future only, positive up to24h/explicit aware UTC wire; no declared future capacity substituted for actual presence.

Existing raw workload page selects a saved plan and asks operator to enter new interval/resource/site/reason; pending original operation/body retained. Author metadata-only future plan on existing135 resource43, failed later resource validation preserves source, two concurrent replacement commands one wins/other source conflict; same replay exact/changed body refused. Cancel own replacement after demonstration, original135 physical fixture unchanged.
