"use client";

import { ChangeEvent, PointerEvent, useMemo, useState } from "react";

type Side = "front" | "right" | "back" | "left";
type FeatureKind = "window" | "door" | "garage_door" | "shutter" | "trim";
type Feature = { id: string; kind: FeatureKind; x: number; y: number; width: number; height: number };

const sides: Side[] = ["front", "right", "back", "left"];
const initialFeatures: Record<Side, Feature[]> = {
  front: [
    { id: "front-door", kind: "door", x: 42, y: 50, width: 16, height: 48 },
    { id: "front-window", kind: "window", x: 12, y: 35, width: 16, height: 24 },
  ],
  right: [],
  back: [],
  left: [],
};

export default function HomePage() {
  const [activeSide, setActiveSide] = useState<Side>("front");
  const [features, setFeatures] = useState(initialFeatures);
  const [selectedId, setSelectedId] = useState("front-door");
  const [photos, setPhotos] = useState<Record<Side, string[]>>({ front: [], right: [], back: [], left: [] });
  const [knownDimension, setKnownDimension] = useState("240");
  const [captureDone, setCaptureDone] = useState<Record<string, boolean>>({});
  const [projectId, setProjectId] = useState("");
  const [message, setMessage] = useState("All changes are local");

  const selected = features[activeSide].find((feature) => feature.id === selectedId);
  const totalPhotos = Object.values(photos).reduce((sum, values) => sum + values.length, 0);
  const captureProgress = useMemo(
    () => sides.filter((side) => photos[side].length >= 2).length,
    [photos],
  );

  function addFeature(kind: FeatureKind) {
    const feature = { id: crypto.randomUUID(), kind, x: 38, y: 34, width: 24, height: 24 };
    setFeatures((current) => ({ ...current, [activeSide]: [...current[activeSide], feature] }));
    setSelectedId(feature.id);
  }

  function updateSelected(patch: Partial<Feature>) {
    setFeatures((current) => ({
      ...current,
      [activeSide]: current[activeSide].map((feature) =>
        feature.id === selectedId ? { ...feature, ...patch } : feature,
      ),
    }));
  }

  function removeSelected() {
    setFeatures((current) => ({
      ...current,
      [activeSide]: current[activeSide].filter((feature) => feature.id !== selectedId),
    }));
    setSelectedId("");
  }

  function moveFeature(event: PointerEvent<HTMLDivElement>, id: string) {
    const canvas = event.currentTarget.parentElement;
    if (!canvas) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    const startX = event.clientX;
    const startY = event.clientY;
    const feature = features[activeSide].find((item) => item.id === id);
    if (!feature) return;
    const onMove = (move: globalThis.PointerEvent) => {
      const nextX = Math.max(0, Math.min(100 - feature.width, feature.x + ((move.clientX - startX) / canvas.clientWidth) * 100));
      const nextY = Math.max(0, Math.min(100 - feature.height, feature.y + ((move.clientY - startY) / canvas.clientHeight) * 100));
      setSelectedId(id);
      setFeatures((current) => ({
        ...current,
        [activeSide]: current[activeSide].map((item) => item.id === id ? { ...item, x: nextX, y: nextY } : item),
      }));
    };
    const onUp = () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }

  function uploadPhotos(event: ChangeEvent<HTMLInputElement>) {
    const urls = Array.from(event.target.files ?? []).map((file) => URL.createObjectURL(file));
    setPhotos((current) => ({ ...current, [activeSide]: [...current[activeSide], ...urls] }));
  }

  function projectPayload() {
    const facade = (side: Side) => ({
      features: features[side].map(({ id: _id, ...feature }) => ({
        ...feature,
        x: feature.x / 100,
        y: (100 - feature.y - feature.height) / 100,
        width: feature.width / 100,
        height: feature.height / 100,
        relief_mm: 1.2,
        color_group: feature.kind === "door" ? "door" : "trim",
      })),
    });
    return {
      project_name: "Operator facade project",
      model: { width_mm: Number(knownDimension) || 240, depth_mm: 190, wall_height_mm: 155, wall_thickness_mm: 4, entrance_hole_diameter_mm: 32 },
      roof: { type: "gable", pitch_degrees: 38, overhang_mm: 10, thickness_mm: 4.5 },
      facades: { front: facade("front"), right: facade("right"), back: facade("back"), left: facade("left") },
      colors: { siding: "warm_gray", trim: "white", door: "blue", roof: "charcoal" },
    };
  }

  async function saveRevision() {
    setMessage("Saving…");
    try {
      const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const response = await fetch(projectId ? `${api}/v1/projects/${projectId}` : `${api}/v1/projects`, {
        method: projectId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(projectPayload()),
      });
      if (!response.ok) throw new Error(await response.text());
      const stored = await response.json();
      setProjectId(stored.project_id);
      setMessage(`Revision ${stored.revision} saved`);
      return stored.project_id as string;
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Save failed");
      return "";
    }
  }

  async function generateModel() {
    const id = projectId || await saveRevision();
    if (!id) return;
    setMessage("Generating six production parts…");
    try {
      const api = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      const response = await fetch(`${api}/v1/projects/${id}/generate`, { method: "POST" });
      if (!response.ok) throw new Error(await response.text());
      const job = await response.json();
      setMessage(job.status === "READY" ? `Model ready · job ${job.job_id.slice(0, 8)}` : `Generation ${job.status.toLowerCase()}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Generation failed");
    }
  }

  const captureItems = [
    "Front straight-on — required",
    "Front/right corner — required",
    "Right straight-on — required",
    "Back/right corner — optional",
    "Back straight-on — required",
    "Back/left corner — optional",
    "Left straight-on — required",
    "Front/left corner — required",
  ];

  return (
    <main>
      <header className="topbar">
        <div><span className="mark">H→B</span><strong>House to Birdhouse</strong></div>
        <div className="status"><span /> Draft project · {totalPhotos} photos</div>
      </header>

      <section className="intro">
        <p className="eyebrow">Operator workspace</p>
        <h1>Trace the house.<br />Build the birdhouse.</h1>
        <p>Upload each elevation, mark architectural details, calibrate one known dimension, then generate the six-part production model.</p>
      </section>

      <nav className="steps" aria-label="Project workflow">
        {["01 Capture", "02 Correct facades", "03 Configure", "04 Preview", "05 Generate"].map((label, index) =>
          <button className={index === 1 ? "active" : ""} key={label}>{label}</button>
        )}
      </nav>

      <section className="workspace">
        <aside className="side-panel">
          <div className="section-heading"><span>Facades</span><b>{captureProgress}/4 ready</b></div>
          {sides.map((side) => (
            <button className={`side-row ${side === activeSide ? "selected" : ""}`} key={side} onClick={() => { setActiveSide(side); setSelectedId(""); }}>
              <span className="side-icon">{side.slice(0, 1).toUpperCase()}</span>
              <span><strong>{side}</strong><small>{photos[side].length} photos · {features[side].length} features</small></span>
              <i>{photos[side].length >= 2 ? "✓" : "·"}</i>
            </button>
          ))}
          <label className="upload-button">Add {activeSide} photos<input type="file" accept="image/*" multiple onChange={uploadPhotos} /></label>
          <div className="calibration">
            <label>Known wall width <span>mm</span></label>
            <input value={knownDimension} onChange={(event) => setKnownDimension(event.target.value)} inputMode="decimal" />
            <small>Use a measurement visible in the active photo.</small>
          </div>
        </aside>

        <section className="editor-panel">
          <div className="editor-toolbar">
            <div><span className="eyebrow">Elevation editor</span><h2>{activeSide} facade</h2></div>
            <div className="feature-actions">
              {(["window", "door", "trim", "shutter"] as FeatureKind[]).map((kind) => <button key={kind} onClick={() => addFeature(kind)}>+ {kind}</button>)}
            </div>
          </div>
          <div className="canvas" style={photos[activeSide][0] ? { backgroundImage: `linear-gradient(rgba(18,24,17,.16),rgba(18,24,17,.16)),url(${photos[activeSide][0]})` } : undefined}>
            {!photos[activeSide][0] && <div className="empty-photo"><span>{activeSide.slice(0, 1).toUpperCase()}</span><p>Upload a straight-on photo to trace this elevation.</p></div>}
            <div className="grid-lines" />
            {features[activeSide].map((feature) => (
              <div
                className={`feature feature-${feature.kind} ${feature.id === selectedId ? "selected-feature" : ""}`}
                key={feature.id}
                style={{ left: `${feature.x}%`, top: `${feature.y}%`, width: `${feature.width}%`, height: `${feature.height}%` }}
                onPointerDown={(event) => moveFeature(event, feature.id)}
              ><span>{feature.kind.replace("_", " ")}</span></div>
            ))}
          </div>
          {selected ? (
            <div className="inspector">
              <strong>{selected.kind}</strong>
              {(["x", "y", "width", "height"] as const).map((field) => <label key={field}>{field}<input type="number" min="0" max="100" value={Math.round(selected[field])} onChange={(event) => updateSelected({ [field]: Number(event.target.value) })} /></label>)}
              <button className="danger" onClick={removeSelected}>Delete</button>
            </div>
          ) : <div className="inspector muted">Select a feature to edit exact normalized dimensions.</div>}
        </section>
      </section>

      <section className="capture-panel">
        <div><p className="eyebrow">Guided capture</p><h2>Eight-view photo checklist</h2><p>Use even daylight, keep the full wall in frame, and retake blurred or heavily obstructed images.</p></div>
        <div className="checklist">
          {captureItems.map((item) => <label key={item}><input type="checkbox" checked={Boolean(captureDone[item])} onChange={() => setCaptureDone((current) => ({ ...current, [item]: !current[item] }))} /><span>{item}</span></label>)}
        </div>
      </section>

      <footer><span>{message} · Production CAD remains physically unvalidated.</span><button onClick={saveRevision}>Save revision</button><button className="primary" onClick={generateModel}>Generate model →</button></footer>
    </main>
  );
}
