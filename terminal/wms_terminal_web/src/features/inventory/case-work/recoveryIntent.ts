import type { Intent } from "./contracts";
import type { OriginalIntent } from "../resource-intents/contracts";
export function recoveryIntent(intent: Intent): OriginalIntent {
 return { domain: "CASE", task_id: intent.task_id, actor: intent.actor, server: intent.server,
  operation_id: intent.body.operation_id, action: intent.body.action, target: intent.actor,
  wire: intent.wire, request_sha256: intent.request_sha256, expected_assignment_version: intent.body.expected_assignment_version };
}
