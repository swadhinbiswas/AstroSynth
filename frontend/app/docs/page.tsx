import { Badge, Card, CardBody } from "@/components/ui/card";

const ROWS: [string, string][] = [
  ["GET /api/v1/health", "Liveness + model-loaded flag"],
  ["GET /api/v1/missions", "Kepler / K2 / TESS catalogue"],
  ["GET /api/v1/datasets?mission=kepler", "Dataset index + archive URLs"],
  ["POST /api/v1/predict", "Classify one observation (10 features)"],
  ["POST /api/v1/batch-predict", "Classify up to 1000 rows"],
  ["GET /api/v1/model-info", "Active model + global importance"],
  ["GET /api/v1/leaderboard", "RF vs XGB vs LGBM vs CatBoost"],
  ["GET /api/v1/metrics", "Active-model summary"],
  ["POST /api/v1/feedback", "Submit a correction label"],
];

export default function DocsPage() {
  return (
    <div className="py-10">
      <Badge className="border-white/20 bg-white/5 text-white/70">DOCUMENTATION</Badge>
      <h1 className="font-display mt-4 text-4xl font-extrabold">API reference</h1>
      <Card className="mt-6"><CardBody>
        <table className="w-full text-sm">
          <thead><tr className="text-left text-white/50"><th>Endpoint</th><th>Description</th></tr></thead>
          <tbody>{ROWS.map(([e, d]) => <tr key={e} className="border-t border-white/10"><td className="py-2 font-mono text-cyan-200">{e}</td><td className="text-white/70">{d}</td></tr>)}</tbody>
        </table>
        <p className="mt-4 text-sm text-white/60">Full OpenAPI + schemas at <span className="font-mono">http://localhost:8000/docs</span>. Demo login: <span className="font-mono">demo@astrosynth.space / demo1234</span>.</p>
      </CardBody></Card>
    </div>
  );
}
