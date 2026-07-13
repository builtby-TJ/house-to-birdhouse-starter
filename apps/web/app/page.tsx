const stages = [
  "Create project",
  "Photograph four sides",
  "Review facade features",
  "Configure roof and colors",
  "Generate six print plates"
];

export default function HomePage() {
  return (
    <main>
      <section className="hero">
        <p className="eyebrow">House-to-Birdhouse</p>
        <h1>Turn guided house photos into a six-part printable model.</h1>
        <p className="lede">
          This interface scaffold will become the customer capture, correction, preview,
          and export workflow.
        </p>
        <button type="button">Create project</button>
      </section>

      <section className="panel">
        <h2>Build workflow</h2>
        <ol>
          {stages.map((stage) => <li key={stage}>{stage}</li>)}
        </ol>
      </section>

      <section className="grid">
        {[
          ["Front wall", "2+ guided photos"],
          ["Back wall", "2+ guided photos"],
          ["Left wall", "2+ guided photos"],
          ["Right wall", "2+ guided photos"],
          ["Roof", "Parametric gable"],
          ["Floor", "Standardized assembly base"]
        ].map(([title, text]) => (
          <article className="card" key={title}>
            <h3>{title}</h3>
            <p>{text}</p>
          </article>
        ))}
      </section>
    </main>
  );
}
