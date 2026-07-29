const BUCKET = "musicos-audio";
const MAX_BYTES = 64 * 1024 * 1024;
const EXPECTED_GITHUB_LOGIN = "hurrisonferd";

function reply(status: number, body: Record<string, unknown>): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function hex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes), (byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("");
}

Deno.serve(async (request: Request) => {
  if (request.method !== "POST") {
    return reply(405, { ok: false, error: "method_not_allowed" });
  }

  const gridToken = request.headers.get("x-grid-token");
  if (!gridToken) {
    return reply(401, { ok: false, error: "missing_grid_token" });
  }

  const github = await fetch("https://api.github.com/user", {
    headers: {
      authorization: `Bearer ${gridToken}`,
      accept: "application/vnd.github+json",
      "user-agent": "JARVIS-MusicOS-Ears",
      "x-github-api-version": "2022-11-28",
    },
  });
  if (!github.ok) {
    return reply(401, { ok: false, error: "github_token_rejected" });
  }
  const identity = await github.json();
  if (identity.login !== EXPECTED_GITHUB_LOGIN) {
    return reply(403, { ok: false, error: "grid_authority_rejected" });
  }

  const objectName = request.headers.get("x-object-name") ?? "";
  if (
    !/^historical\/[^/\u0000-\u001f]{1,220}\.mp3$/i.test(objectName)
  ) {
    return reply(400, { ok: false, error: "invalid_object_name" });
  }
  if (request.headers.get("content-type")?.split(";")[0] !== "audio/mpeg") {
    return reply(415, { ok: false, error: "audio_mpeg_required" });
  }

  const declaredLength = Number(request.headers.get("content-length") ?? "0");
  if (declaredLength > MAX_BYTES) {
    return reply(413, { ok: false, error: "source_too_large" });
  }

  const audio = await request.arrayBuffer();
  if (audio.byteLength === 0 || audio.byteLength > MAX_BYTES) {
    return reply(413, { ok: false, error: "invalid_source_size" });
  }
  const signature = new Uint8Array(audio.slice(0, 3));
  const isId3 = signature[0] === 0x49 && signature[1] === 0x44 &&
    signature[2] === 0x33;
  const isFrame = signature[0] === 0xff && (signature[1] & 0xe0) === 0xe0;
  if (!isId3 && !isFrame) {
    return reply(415, { ok: false, error: "invalid_mp3_signature" });
  }

  const sha256 = hex(await crypto.subtle.digest("SHA-256", audio));
  const expectedSha = request.headers.get("x-content-sha256");
  if (expectedSha && expectedSha.toLowerCase() !== sha256) {
    return reply(422, { ok: false, error: "sha256_mismatch" });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL");
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!supabaseUrl || !serviceKey) {
    return reply(500, { ok: false, error: "storage_not_configured" });
  }

  const encodedName = objectName.split("/").map(encodeURIComponent).join("/");
  const stored = await fetch(
    `${supabaseUrl}/storage/v1/object/${BUCKET}/${encodedName}`,
    {
      method: "POST",
      headers: {
        authorization: `Bearer ${serviceKey}`,
        apikey: serviceKey,
        "content-type": "audio/mpeg",
        "x-upsert": "true",
      },
      body: audio,
    },
  );
  if (!stored.ok) {
    return reply(502, {
      ok: false,
      error: "storage_write_failed",
      storage_status: stored.status,
    });
  }

  return reply(200, {
    ok: true,
    bucket: BUCKET,
    object: objectName,
    bytes: audio.byteLength,
    sha256,
    authority: EXPECTED_GITHUB_LOGIN,
  });
});
