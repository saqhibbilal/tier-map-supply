import { LEGEND_ITEMS } from "../utils/tierColors";
import styles from "./Legend.module.css";

export default function Legend() {
  return (
    <div className={styles.legend}>
      <div className={styles.title}>Tiers</div>
      <div className={styles.subtitle}>Tier 1 = direct supplier; higher = further upstream.</div>
      <div className={styles.subtitle}>Click a node to highlight its connections.</div>
      {LEGEND_ITEMS.map(({ label, color }) => (
        <div key={label} className={styles.item}>
          <span className={styles.dot} style={{ backgroundColor: color }} />
          <span>{label}</span>
        </div>
      ))}
    </div>
  );
}
