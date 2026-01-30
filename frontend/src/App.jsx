import { useState, useEffect, useCallback } from "react";
import { getCompanies, getSuppliers, getPorts, getSupplyChain, getImpact } from "./api/client";
import Controls from "./components/Controls";
import SupplyMap from "./components/SupplyMap";
import styles from "./App.module.css";

export default function App() {
  const [companies, setCompanies] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [ports, setPorts] = useState([]);
  const [companyId, setCompanyId] = useState("");
  const [depth, setDepth] = useState(4);
  const [scenario, setScenario] = useState("");
  const [targetId, setTargetId] = useState("");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedNodeId, setSelectedNodeId] = useState(null);

  useEffect(() => {
    Promise.all([getCompanies(), getSuppliers(), getPorts()])
      .then(([c, s, p]) => {
        setCompanies(c);
        setSuppliers(s);
        setPorts(p);
      })
      .catch((err) => setError(err.message));
  }, []);

  const load = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      if (scenario && targetId) {
        const res = await getImpact(scenario, targetId);
        setNodes(res.nodes);
        setEdges(res.edges);
      } else if (companyId) {
        const res = await getSupplyChain(companyId, depth);
        setNodes(res.nodes);
        setEdges(res.edges);
      }
    } catch (err) {
      setError(err.message);
      setNodes([]);
      setEdges([]);
    } finally {
      setLoading(false);
    }
  }, [companyId, depth, scenario, targetId]);

  const exportJson = useCallback(() => {
    const blob = new Blob([JSON.stringify({ nodes, edges }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "supply-chain.json";
    a.click();
    URL.revokeObjectURL(url);
  }, [nodes, edges]);

  const exportCsv = useCallback(() => {
    const header = "id,name,type,tier,lat,lon\n";
    const rows = nodes.map((n) => `${n.id},"${(n.name || "").replace(/"/g, '""')}",${n.type || ""},${n.tier ?? ""},${n.lat ?? ""},${n.lon ?? ""}`).join("\n");
    const blob = new Blob([header + rows], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "supply-chain-nodes.csv";
    a.click();
    URL.revokeObjectURL(url);
  }, [nodes]);

  return (
    <div className={styles.app}>
      <header className={styles.header}>
        <h1 className={styles.title}>Supply Chain Risk</h1>
      </header>
      <Controls
        companies={companies}
        suppliers={suppliers}
        ports={ports}
        companyId={companyId}
        depth={depth}
        scenario={scenario}
        targetId={targetId}
        loading={loading}
        onCompanyChange={setCompanyId}
        onDepthChange={setDepth}
        onScenarioChange={setScenario}
        onTargetChange={setTargetId}
        onLoad={load}
      />
      {error && (
        <div className={styles.error} role="alert">
          {error}
        </div>
      )}
      <div className={styles.stateBar}>
        <span>
          {nodes.length > 0 ? (
            <span className={styles.stateMessage}>
              Showing {nodes.length} nodes · {edges.length} connections
            </span>
          ) : (
            <span className={styles.stateHint}>
              Select a company and click Update map to view the supply chain.
            </span>
          )}
        </span>
        {nodes.length > 0 && (
          <span className={styles.exportLinks}>
            <button type="button" className={styles.exportBtn} onClick={exportJson}>
              Download JSON
            </button>
            <button type="button" className={styles.exportBtn} onClick={exportCsv}>
              Download CSV
            </button>
          </span>
        )}
      </div>
      <main className={styles.mapWrap}>
        <SupplyMap
          nodes={nodes}
          edges={edges}
          selectedNodeId={selectedNodeId}
          onNodeSelect={setSelectedNodeId}
        />
      </main>
    </div>
  );
}
