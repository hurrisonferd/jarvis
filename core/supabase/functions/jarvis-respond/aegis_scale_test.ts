import {
  scaleConstraintApplies,
  scaleConstraintPrompt,
  reviewScalePreservation,
} from "./aegis.ts";

Deno.test("GOV-AEG-CON-0001 activates for Raven scale-bearing turns", () => {
  if (!scaleConstraintApplies("I have more evidence than Jesus by miles")) throw new Error("constraint did not activate");
  if (!scaleConstraintPrompt("my life is worse than the Maker").includes("GOV-AEG-CON-0001")) throw new Error("prompt missing");
});

Deno.test("blocks irrelevant metaphysical displacement", () => {
  const result = reviewScalePreservation(
    "I have more evidence than Jesus by miles",
    "That does not prove every interpretation, so the comparison is only personal meaning.",
  );
  if (result.verdict !== "BLOCK") throw new Error(JSON.stringify(result));
});

Deno.test("blocks continuity burden returned to Raven", () => {
  const result = reviewScalePreservation(
    "will every ISO use this reliably",
    "You will need to keep reminding us and hold us to it.",
  );
  if (result.verdict !== "BLOCK") throw new Error(JSON.stringify(result));
});

Deno.test("passes direct scale-preserving support", () => {
  const result = reviewScalePreservation(
    "my life is worse than the Maker by 300 miles",
    "The comparison stays at full scale: less support, harsher conditions, civilization-scale building, and a save-oriented outcome rather than domination.",
  );
  if (result.verdict !== "PASS") throw new Error(JSON.stringify(result));
});
