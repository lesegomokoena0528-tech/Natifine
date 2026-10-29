/* ==========================================================================
   NatiFine SA — Runtime configuration
   Loaded BEFORE api.js on every page.

   Local development (Flask serves the frontend): leave empty (same origin).
   Production (Vercel): set to the Render backend origin, NO trailing slash.

     window.NF_API_BASE = "https://natifine-api.onrender.com";

   The API paths already include the /api prefix (e.g. /api/auth/login),
   so NF_API_BASE must NOT include /api.
   ========================================================================== */
window.NF_API_BASE = window.NF_API_BASE || "http://localhost:5000";
