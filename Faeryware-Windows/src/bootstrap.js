const params = new URLSearchParams(window.location.search);

if (params.get("surface") === "army") {
  await import("./army.js");
} else {
  await import("./main.js");
}
