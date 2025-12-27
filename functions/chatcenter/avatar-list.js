export async function onRequest(context) {
  try {
    // List all files in the avatar directory
    const list = await context.env.ASSETS.list({ prefix: "chatcenter/avatar/" });
    
    // Filter for SVG files and extract just the filenames
    const files = list.objects
      .map(obj => obj.key)
      .filter(key => key.startsWith("chatcenter/avatar/") && key.endsWith('.svg'))
      .map(key => key.replace("chatcenter/avatar/", ""))
      .filter(name => name.trim() !== "");

    return new Response(JSON.stringify(files), {
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*" // Allow CORS if needed
      }
    });

  } catch (err) {
    console.error("Avatar list error:", err);
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { 
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
      }
    });
  }
}
