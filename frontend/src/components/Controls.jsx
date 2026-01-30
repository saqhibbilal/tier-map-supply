import styles from "./Controls.module.css";

export default function Controls({
  companies,
  suppliers,
  ports,
  companyId,
  depth,
  scenario,
  targetId,
  loading,
  onCompanyChange,
  onDepthChange,
  onScenarioChange,
  onTargetChange,
  onLoad,
}) {
  const canLoadSupplyChain = companyId && scenario === "";
  const canLoadImpact = scenario && targetId;
  const canLoad = canLoadSupplyChain || canLoadImpact;

  return (
    <div className={styles.controls}>
      <div className={styles.row}>
        <label className={styles.label}>Focal company</label>
        <select
          className={styles.select}
          value={companyId}
          onChange={(e) => onCompanyChange(e.target.value)}
          disabled={loading}
        >
          <option value="">Choose company</option>
          {(companies || []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>
      <div className={styles.row}>
        <label className={styles.label}>Upstream tiers</label>
        <select
          className={styles.select}
          value={depth}
          onChange={(e) => onDepthChange(Number(e.target.value))}
          disabled={loading}
        >
          {[1, 2, 3, 4].map((d) => (
            <option key={d} value={d}>
              {d} tier{d !== 1 ? "s" : ""}
            </option>
          ))}
        </select>
      </div>
      <div className={styles.row}>
        <label className={styles.label}>View</label>
        <select
          className={styles.select}
          value={scenario}
          onChange={(e) => {
            onScenarioChange(e.target.value);
            onTargetChange("");
          }}
          disabled={loading}
        >
          <option value="">Supply chain map</option>
          <option value="supplier_failure">If supplier fails</option>
          <option value="port_closure">If port closes</option>
        </select>
      </div>
      {scenario === "supplier_failure" && (
        <div className={styles.row}>
          <label className={styles.label}>Which supplier</label>
          <select
            className={styles.select}
            value={targetId}
            onChange={(e) => onTargetChange(e.target.value)}
            disabled={loading}
          >
            <option value="">Choose supplier</option>
            {(suppliers || []).map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
        </div>
      )}
      {scenario === "port_closure" && (
        <div className={styles.row}>
          <label className={styles.label}>Which port</label>
          <select
            className={styles.select}
            value={targetId}
            onChange={(e) => onTargetChange(e.target.value)}
            disabled={loading}
          >
            <option value="">Choose port</option>
            {(ports || []).map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      )}
      <div className={styles.row}>
        <button
          className={styles.button}
          onClick={onLoad}
          disabled={!canLoad || loading}
        >
          {loading ? "Loading…" : "Update map"}
        </button>
      </div>
    </div>
  );
}
