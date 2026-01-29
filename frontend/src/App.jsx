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
      <main className={styles.mapWrap}>
        <SupplyMap nodes={nodes} edges={edges} />
      </main>
    </div>
  );
}
