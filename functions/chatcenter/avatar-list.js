export async function onRequest(context) {
  try {
    // Avatar folder inside Pages assets
    const list = await context.env.ASSETS.list({ prefix: "avatar/" });

    const files = list.objects
      .map(obj => obj.key.replace("avatar/", ""))
      .filter(name => name.trim() !== "");

    return new Response(JSON.stringify(files), {
      headers: { "Content-Type": "application/json" }
    });

  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}
