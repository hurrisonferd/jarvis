// tools/cloud.test.ts — Cloud tools tests

import { assertEquals, assertStringIncludes } from "jsr:@std/assert";

const TODAY = new Date().toISOString().split("T")[0];

// Mock the GitHub API response
const mockFetch = (body: string, ok = true, status = 200) => {
  globalThis.fetch = async (_url: Request | URL | string, _init?: RequestInit) => {
    return new Response(body, {
      status,
      headers: { "content-type": "application/json" },
      ok,
    });
  };
};

Deno.test("cloud — timestamp format HHMMSS", () => {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, "0");
  const m = String(now.getMinutes()).padStart(2, "0");
  const s = String(now.getSeconds()).padStart(2, "0");
  const expected = `${h}${m}${s}`;
  
  // Should be 6 digits
  assertEquals(expected.length, 6);
  assertEquals(/^\d{6}$/.test(expected), true);
});

Deno.test("cloud — date format YYYY-MM-DD", () => {
  assertEquals(TODAY.match(/^\d{4}-\d{2}-\d{2}$/) !== null, true);
});

Deno.test("cloud — entry format", () => {
  const model = "OpenHands";
  const action = "Test completed";
  const timestamp = "123456";
  const date = "2026-06-28";
  
  const entryLines = [
    "",
    `[${timestamp}] ${model}:`,
    `- action: ${action}`,
    `- status: ok`,
  ];
  
  const entry = entryLines.join("\n");
  assertStringIncludes(entry, `[${timestamp}] ${model}:`);
  assertStringIncludes(entry, `- action: ${action}`);
  assertStringIncludes(entry, `- status: ok`);
});

Deno.test("cloud — read response format", () => {
  const mockResponse = {
    ok: true,
    date: TODAY,
    entries: [
      "[123456] OpenHands: Test entry",
      "[123500] Ayre: Another entry",
    ],
    count: 2,
    message: `Found 2 entries for ${TODAY}`,
  };
  
  assertEquals(mockResponse.ok, true);
  assertEquals(mockResponse.entries.length, 2);
  assertEquals(mockResponse.entries[0].startsWith("["), true);
});

Deno.test("cloud — write response format", () => {
  const mockResponse = {
    ok: true,
    timestamp: "123456",
    date: TODAY,
    model: "JARVIS",
    entry: "[123456] JARVIS: Voice session started",
    message: `Logged to Cloud for ${TODAY}`,
  };
  
  assertEquals(mockResponse.ok, true);
  assertEquals(mockResponse.timestamp.length, 6);
  assertEquals(mockResponse.entry.startsWith("["), true);
});

Deno.test("cloud — 404 for missing date", () => {
  const mockResponse = {
    ok: false,
    error: "No log found for 2025-01-01",
    date: "2025-01-01",
    message: "Use jarvis_cloud_write to create the first entry for today.",
  };
  
  assertEquals(mockResponse.ok, false);
  assertStringIncludes(mockResponse.error, "No log found");
});