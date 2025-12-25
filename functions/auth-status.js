export async function onRequest(context) {
  const workerUrl = "https://broad-sound-fdb7.raceanalyst.workers.dev/auth-status";

  const req = new Request(workerUrl, {
    method: "GET",
    headers: {
      "cf-access-authenticated-user-email":
        context.request.headers.get("cf-access-authenticated-user-email") || "",
      "cf-access-authenticated-user-name":
        context.request.headers.get("cf-access-authenticated-user-name") || "",
      "Cookie": context.request.headers.get("Cookie") || "",
      "User-Agent": context.request.headers.get("User-Agent") || "",
      "Accept": "application/json"
    }
  });

  const workerResponse = await fetch(req);

  return new Response(workerResponse.body, {
    status: workerResponse.status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
