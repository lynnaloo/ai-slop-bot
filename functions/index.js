const { onRequest } = require("firebase-functions/v2/https");
const { initializeApp } = require("firebase-admin/app");
const { getAuth } = require("firebase-admin/auth");
const { GoogleAuth } = require("google-auth-library");

initializeApp();

const CLOUD_RUN_URL = "https://ai-slop-api-lxxfdfgvoq-uc.a.run.app";
const auth = new GoogleAuth();

const CORS_ORIGIN = [
  "http://localhost:5173",
  "https://ai-slop-detector.web.app",
  "https://ehc-c-buskey-506b97.web.app",
];

exports.api = onRequest(
  { region: "us-central1", cors: CORS_ORIGIN },
  async (req, res) => {
    // Verify the Firebase ID token from the Authorization header
    const authHeader = req.headers.authorization ?? "";
    const idToken = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : null;

    if (!idToken) {
      res.status(401).json({ detail: "Missing authorization token" });
      return;
    }

    try {
      await getAuth().verifyIdToken(idToken);
    } catch {
      res.status(401).json({ detail: "Invalid authorization token" });
      return;
    }

    // Get a Google OIDC token scoped to the Cloud Run service
    const client = await auth.getIdTokenClient(CLOUD_RUN_URL);
    const headers = await client.getRequestHeaders();

    // Forward the request to Cloud Run
    const targetUrl = `${CLOUD_RUN_URL}${req.path}`;
    const fetchRes = await fetch(targetUrl, {
      method: req.method,
      headers: {
        ...headers,
        // Forward content-type but NOT authorization (we replaced it above)
        ...(req.headers["content-type"] && {
          "content-type": req.headers["content-type"],
        }),
      },
      body: req.method !== "GET" && req.method !== "HEAD" ? req : undefined,
    });

    const body = Buffer.from(await fetchRes.arrayBuffer());
    res.status(fetchRes.status);
    fetchRes.headers.forEach((v, k) => {
      if (!["content-encoding", "transfer-encoding"].includes(k)) res.set(k, v);
    });
    res.send(body);
  }
);
