# Pachinko Bounce — 3D Core

Top-down, tap-to-spawn ball physics. Power-ups, multipliers, trenches with real
depth, satisfying 3D bounce + haptics. **Godot 4.x (Jolt physics).**

## Why 3D (decided 2026-05-30)
The bounce/physics that fought us in 2D Unity is free in 3D: a `RigidBody3D` +
`PhysicsMaterial(bounce)` in a walled space does restitution correctly. Trenches
with depth = real geometry, not faked. A top-down **orthographic** camera keeps
the 2D arcade feel with true 3D bounce underneath. Confined space = stable physics.

## Scene setup (do this once in the Godot editor)
```
Main (Node3D)                      attach: (game manager later)
├── Camera3D                       Projection = Orthogonal; rotate X = -90 (look down);
│                                  position above arena; Size ~ arena width
├── DirectionalLight3D             angle it for nice shadows in the trenches
├── Arena (Node3D)
│   ├── Floor   (StaticBody3D + CollisionShape3D BoxShape)   thin wide box
│   ├── Wall_N/S/E/W (StaticBody3D + Box)                    contain the play space
│   └── Trench  (StaticBody3D + meshes)                      wells with DEPTH (the juice)
├── BallContainer (Node3D)         spawned balls live here
├── Spawner (Node3D)               attach operations/scripts/spawner.gd
└── HUD (CanvasLayer)              score + multiplier labels (later)
```
Make a **Ball** scene: `RigidBody3D` (attach `operations/scripts/ball.gd`) + `MeshInstance3D`
(SphereMesh) + `CollisionShape3D` (SphereShape). Save as `ball.tscn`, assign it to
the Spawner's `ball_scene`.

Multiplier wells: `Area3D` + `operations/scripts/multiplier_zone.gd`, dropped into the trenches.

## The trap to avoid
Leave **Continuous CD OFF** on the ball — it breaks `PhysicsMaterial.bounce` in Godot.

## Files
- `operations/scripts/ball.gd` — the ball; bounce material set in code + haptic on impact.
- `operations/scripts/spawner.gd` — tap → raycast to floor → drop a ball (the tap spawner, done right).
- `operations/scripts/multiplier_zone.gd` — trench wells that score, multiply, and pop the ball.

Tune feel with `bounce` (0.7–0.9), drop height, and the well `kick`. That's the dial
for "satisfying."
