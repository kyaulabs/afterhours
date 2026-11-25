# Vanilla++ baseline

The first AfterHours build keeps vanilla survival progression and adds structures to discover, environmental sound, and character animation. Dungeons and Taverns already changes world generation. Start the first playthrough with its stock structure frequency so another structure pack does not obscure how often its buildings appear.

## Graphics and sound

The reference machine has a Ryzen 7 3700X, 64 GiB of RAM, and a GeForce RTX 5070 with 12 GiB of VRAM driving a 3440 × 1440 display. Prism uses Java 25 with a 2–6 GiB heap. Minecraft starts on OpenGL at a 90 FPS cap, with VSync off, 16 chunks visible, and 8 chunks simulated. The archive sets the game options and shader. Heap sizes belong to the launcher instance.

| Mods | AfterHours setting |
| --- | --- |
| Iris, Sodium, Sodium Extra | Iris 1.11.7, Sodium 0.9.2, and Sodium Extra 0.9.5. This pair satisfies Iris and Sodium Extra on 26.3. Keep Sodium’s driver workarounds and automatic chunk workers. |
| Complementary Unbound | r5.10, High. The preset uses 192-block shadows and enables entity shadows. Select Medium in Iris if GPU-heavy scenes need more headroom. |
| C2ME, Lithium | Use the pinned versions’ worker scheduling and optimization defaults. For stalls limited to exploration, reduce render distance to 12 chunks and compare a second pass over the same route. |
| Particle Rain | Budget 900 particles with a 1.25 storm multiplier. The mod handles rain and snow particles and defers tinting to the shader. |
| AmbientSounds, CreativeCore | Keep the built-in ambience engine and CreativeCore defaults. Start ambient audio at 65% and the weather channel at 55% to leave room for nearby mobs and blocks. |

## Survival, camera, and interface

| Mods | AfterHours setting |
| --- | --- |
| Dungeons and Taverns | Enable the bundled structures and loot. Judge spacing in newly generated chunks. |
| First-person Model, Not Enough Animations, 3D Skin Layers | Use the first-person body with dynamic positioning, stock animations, and fast skin rendering. The default skin detail cutoff is 14 blocks. |
| Entity Model Features, Entity Texture Features | Keep the pinned resource-pack compatibility defaults. The baseline uses vanilla entity assets. |
| Unbound Third Person, Third Person Nametags | The Survival camera starts four blocks back, keeps the front view in the camera cycle, and leaves combat lock-on off. Nametags use the mod’s defaults. |
| Jade | Show block and entity information at 85% scale. Hide duplicate mod-name lines in item tooltips. |
| Just Enough Items, MezzConfig | Limit the ingredient list to six columns and automatically hide unnecessary navigation. MezzConfig uses its default client profile. |
| Enchantment Descriptions, PrickleMC | Hold Shift to read descriptions. Prickle reads the supplied settings. |
| Mod Menu | Exclude libraries and child modules from the displayed count and hide the update badge. |
| Fabric API, Placeholder API | Use the versions pinned in the manifest. Their dependent mods supply the player-facing behavior. |

## Suggested additions

Start with the first three. They help with everyday decisions and inventory handling from the first meal through end-game storage. The remaining choices add atmosphere or multiplayer polish. Each link points to a Fabric build for **Minecraft 26.3**. These are candidates for the next playtest.

| Order | Candidate | What to try |
| --- | --- | --- |
| 1 | AppleSkin | Compare two foods on the hotbar and see how much hunger and saturation each restores. Use the server component for accurate saturation on multiplayer. [3.0.10](https://modrinth.com/mod/appleskin/version/PHjDtQay) |
| 2 | Mouse Tweaks | Drag stacks through a crafting grid and scroll items between a chest and inventory. Test scrolling beside the JEI panel. [2.31](https://modrinth.com/mod/mouse-tweaks/version/LeMuMhLv) |
| 3 | Shulker Box Tooltip | Hold Shift over a shulker to preview its contents before placing it. Check the interaction with enchanted-item tooltips. [5.4.3](https://modrinth.com/mod/shulkerboxtooltip/version/60krd8u8) |
| 4 | Presence Footsteps | Walk a route across timber, grass, and stone, then repeat it in rain. Listen for footsteps against AmbientSounds and Particle Rain. [1.14.1](https://modrinth.com/mod/presence-footsteps/version/PV68dcBA) |
| 5 | Continuity | Try its bundled connected-texture pack on a glass wall and compare the seams with Complementary enabled. [3.0.1](https://modrinth.com/mod/continuity/version/Jt2sCWTQ) |
| 6 | Chat Heads | Put player faces beside chat messages on the first multiplayer playtest. [1.3.3](https://modrinth.com/mod/chat-heads/version/9O2ZSOkh) |
