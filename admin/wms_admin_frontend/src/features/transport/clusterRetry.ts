type ClusterBody = {
  stdate: string; transtype: string; vehicle: string | null;
  driver_id: number | null; dock: string | null; ware_ids: number[] | null;
};
type Saved = { district: string; body: ClusterBody; operation_id: string };
type Result = { task_id: number; st_count: number; warnings: string[] };

export async function submitCluster(
  send: <T>(path: string, init: RequestInit) => Promise<T>,
  scope: { api: string; actor: string }, district: string, body: ClusterBody,
): Promise<Result> {
  const key = "retailcase.cluster.pending:" + JSON.stringify([scope.api, scope.actor]);
  const raw = localStorage.getItem(key);
  const saved: Saved = raw ? JSON.parse(raw) : {
    district, body, operation_id: "CLUSTER.UI:" + crypto.randomUUID(),
  };
  if (saved.district !== district || JSON.stringify(saved.body) !== JSON.stringify(body)) {
    throw new Error("Ожидает подтверждения предыдущий запрос. Повторите исходные параметры: " +
      JSON.stringify({ район: saved.district, ...saved.body }));
  }
  // Save before sending: storage failures must not cause an untracked mutation.
  localStorage.setItem(key, JSON.stringify(saved));
  try {
    const result = await send<Result>(
      "/api/admin/transport/clusters/" + encodeURIComponent(saved.district) + "/create-task",
      { method: "POST", body: JSON.stringify({ ...saved.body, operation_id: saved.operation_id }) },
    );
    localStorage.removeItem(key);
    return result;
  } catch (error) {
    const message = String(error instanceof Error ? error.message : error);
    // These native input/business failures roll back the entire command.
    // Auth loss, network errors and 5xx do not establish the prior outcome.
    if (/^(400|404|409|422):/.test(message)) localStorage.removeItem(key);
    throw error;
  }
}
