/**
 * Marker color by node type and tier (for map and legend).
 */
export function getNodeColor(node) {
  const { type, tier } = node;
  if (type === "Company") return "#0f172a";
  if (type === "Supplier" && tier != null) {
    const tierColors = { 1: "#15803d", 2: "#1d4ed8", 3: "#c2410c", 4: "#b91c1c" };
    return tierColors[tier] ?? "#64748b";
  }
  if (type === "Port") return "#64748b";
  if (type === "Factory") return "#475569";
  if (type === "Country") return "#94a3b8";
  return "#64748b";
}

export const LEGEND_ITEMS = [
  { label: "Company", color: "#0f172a" },
  { label: "Tier 1", color: "#15803d" },
  { label: "Tier 2", color: "#1d4ed8" },
  { label: "Tier 3", color: "#c2410c" },
  { label: "Tier 4", color: "#b91c1c" },
  { label: "Port", color: "#64748b" },
  { label: "Factory", color: "#475569" },
];
