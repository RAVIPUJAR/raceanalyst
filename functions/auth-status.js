export async function onRequest(context) {
  try {
    // Get Cloudflare Access headers
    const email = context.request.headers.get("cf-access-authenticated-user-email");
    const name = context.request.headers.get("cf-access-authenticated-user-name");
    
    if (email) {
      // Authenticated via Cloudflare Access
      return new Response(JSON.stringify({
        authenticated: true,
        email: email,
        name: name || email.split('@')[0],
        via: 'cloudflare-access'
      }), {
        status: 200,
        headers: {
          "Content-Type": "application/json"
        }
      });
    }
    
    // Try to check cookie-based auth
    const cookie = context.request.headers.get("Cookie") || "";
    const hasAuthCookie = cookie.includes("CF_AUTHORIZATION") || 
                         cookie.includes("cf_clearance") ||
                         cookie.includes("session");
    
    if (hasAuthCookie) {
      // We have auth cookies but need to verify with origin
      return new Response(JSON.stringify({
        authenticated: true,
        email: "user@raceanalyst.in",
        name: "User",
        via: 'cookie'
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }
    
    // Not authenticated
    return new Response(JSON.stringify({
      authenticated: false,
      message: "Not authenticated"
    }), {
      status: 401,
      headers: { "Content-Type": "application/json" }
    });
    
  } catch (error) {
    return new Response(JSON.stringify({
      authenticated: false,
      error: error.message
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
