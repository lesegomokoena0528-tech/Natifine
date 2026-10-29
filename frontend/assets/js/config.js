/* ==========================================================================
   NatiFine SA — Runtime configuration
   Loaded BEFORE api.js on every page.

   Local development and Vercel Services both serve the frontend and backend
   from the same origin, so the default empty value is correct.

   To point at a separate backend (e.g. Render), set an absolute origin here:
     window.NF_API_BASE = "https://natifine-api.onrender.com";

   API paths already include the /api prefix (e.g. /api/auth/login), so
   NF_API_BASE must NOT include /api.
   ========================================================================== */
window.NF_API_BASE = window.NF_API_BASE || "";
