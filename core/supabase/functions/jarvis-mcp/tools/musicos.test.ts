import { assert, assertEquals, assertMatch } from "jsr:@std/assert@1";
import { compileMusicIntent } from "./musicos.ts";

Deno.test("MusicOS TypeScript compiler holds the Raven default contract", () => {
  const result = compileMusicIntent({
    intent: "neon race with elastic bass and dry drums",
    styles: ["synthpop rock", "PS1 racing-game drive"],
  });
  assertEquals(result.bpm, 102);
  assertEquals(result.key, "F# minor");
  assert(result.physics.includes("forward momentum"));
  assert(result.physics.includes("snap-back"));
  assert(result.physics.includes("subdivision precision"));
  assertMatch(result.prompt, /This track conveys/);
  assert(result.prompt.endsWith("102 BPM."));
});

Deno.test("MusicOS compiler translates named influences and platform language", () => {
  const result = compileMusicIntent({
    intent: "Copeland and Bonham drums for Suno, no vocals",
  });
  assert(!/Copeland|Bonham|Suno/i.test(result.prompt));
  assertMatch(result.prompt, /articulate hi-hat intelligence/);
  assertMatch(result.prompt, /heavyweight kick-snare authority/);
  assertMatch(result.prompt, /instrumental focus/);
});
