import { useMemo, useEffect } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import { getNodeColor } from "../utils/tierColors";
import Legend from "./Legend";
import "leaflet/dist/leaflet.css";

const WORLD_CENTER = [20, 0];
const WORLD_ZOOM = 2;

function FitBounds({ nodes }) {
  const map = useMap();
  const withCoords = useMemo(() => nodes.filter((n) => n.lat != null && n.lon != null), [nodes]);
  useEffect(() => {
    if (withCoords.length === 0) return;
    const bounds = L.latLngBounds(withCoords.map((n) => [n.lat, n.lon]));
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 10 });
  }, [map, withCoords]);
  return null;
}

function NodeMarkers({ nodes, edges, nodeById, selectedNodeId, onNodeSelect }) {
  const suppliesToByNode = useMemo(() => {
    const m = {};
    (edges || []).forEach((e) => {
      const toName = nodeById[e.to_id]?.name;
      if (!toName) return;
      if (!m[e.from_id]) m[e.from_id] = [];
      m[e.from_id].push(toName);
    });
    return m;
  }, [edges, nodeById]);

  return nodes
    .filter((n) => n.lat != null && n.lon != null)
    .map((node) => {
      const suppliesTo = suppliesToByNode[node.id];
      const suppliesLine = suppliesTo?.length ? `Supplies to: ${suppliesTo.slice(0, 3).join(", ")}${suppliesTo.length > 3 ? "…" : ""}` : null;
      const isSelected = selectedNodeId === node.id;
      return (
        <CircleMarker
          key={node.id}
          center={[node.lat, node.lon]}
          radius={node.type === "Company" ? 10 : 7}
          pathOptions={{
            fillColor: getNodeColor(node),
            color: isSelected ? "#0f172a" : "#fff",
            weight: isSelected ? 3 : 1.5,
            fillOpacity: 0.9,
          }}
          eventHandlers={{ click: () => onNodeSelect?.(node.id === selectedNodeId ? null : node.id) }}
        >
          <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
            <strong>{node.name}</strong>
            <br />
            {node.type}
            {node.tier != null ? ` · Tier ${node.tier}` : ""}
            {suppliesLine && (
              <>
                <br />
                <span style={{ fontSize: "11px", color: "#64748b" }}>{suppliesLine}</span>
              </>
            )}
          </Tooltip>
          <Popup>
            <strong>{node.name}</strong>
            <br />
            {node.type}
            {node.tier != null ? ` · Tier ${node.tier}` : ""}
            {suppliesLine && (
              <>
                <br />
                <span style={{ fontSize: "11px", color: "#64748b" }}>{suppliesLine}</span>
              </>
            )}
          </Popup>
        </CircleMarker>
      );
    });
}

function EdgePolylines({ edges, nodeById, selectedNodeId }) {
  return edges
    .filter((e) => {
      const from = nodeById[e.from_id];
      const to = nodeById[e.to_id];
      return from?.lat != null && from?.lon != null && to?.lat != null && to?.lon != null;
    })
    .map((e, i) => {
      const from = nodeById[e.from_id];
      const to = nodeById[e.to_id];
      const positions = [
        [from.lat, from.lon],
        [to.lat, to.lon],
      ];
      const isRisk = e.type === "SUPPLIES_TO" || e.type === "DEPENDS_ON";
      const isHighlighted = selectedNodeId && (e.from_id === selectedNodeId || e.to_id === selectedNodeId);
      return (
        <Polyline
          key={`${e.from_id}-${e.to_id}-${i}`}
          positions={positions}
          pathOptions={{
            color: isHighlighted ? (isRisk ? "#b91c1c" : "#0f172a") : isRisk ? "#b91c1c" : "#64748b",
            weight: isHighlighted ? 4 : 2,
            opacity: isHighlighted ? 0.95 : 0.4,
          }}
        />
      );
    });
}

export default function SupplyMap({ nodes = [], edges = [], selectedNodeId, onNodeSelect }) {
  const nodeById = useMemo(() => {
    const map = {};
    nodes.forEach((n) => (map[n.id] = n));
    return map;
  }, [nodes]);

  const hasData = nodes.length > 0;

  return (
    <div className="supply-map" style={{ width: "100%", height: "100%", minHeight: 400 }}>
      <MapContainer
        center={WORLD_CENTER}
        zoom={WORLD_ZOOM}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {hasData && <FitBounds nodes={nodes} />}
        <NodeMarkers
          nodes={nodes}
          edges={edges}
          nodeById={nodeById}
          selectedNodeId={selectedNodeId}
          onNodeSelect={onNodeSelect}
        />
        <EdgePolylines edges={edges} nodeById={nodeById} selectedNodeId={selectedNodeId} />
        <Legend />
      </MapContainer>
    </div>
  );
}
