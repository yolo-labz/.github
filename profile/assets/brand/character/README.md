# Gremlin, 3D

One rigged model and a picture of each state.

| File | What |
|---|---|
| `gremlin.glb` | The character, 225 KB. One skeleton, five animation clips: `idle`, `working`, `paused`, `loading`, `asleep`. Mesh data is meshopt-compressed; there are no textures. |
| `gremlin-<state>.webp`, `.avif` | A still per state, 640 px, transparent background. |
| `gremlin-turntable.webp`, `.avif` | The idle pose, one turn in 24 frames at 12 fps, 400 px. |
| `viewer.html` | A page that loads the model and plays a clip. |
| `manifest.json` | Size and sha256 of every file, and the alt text to use. |

Colours are the kit's own (`model/params.json`). The skin is `#a6e3a1`, the eye
pupils and the code marks are `#cba6f7`, and the 2D mark wins if they ever disagree.

## Load it

```js
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";

const loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
const gltf = await loader.loadAsync("gremlin.glb");
new AnimationMixer(gltf.scene).clipAction(gltf.animations.find((c) => c.name === "working")).play();
```

`<model-viewer src="gremlin.glb" animation-name="working" autoplay camera-controls>`
works as well, with `meshopt-decoder` set on the element.

## Check

```sh
make web-verify     # hashes, 1.5 MB limit, five clips, palette
```

Copy the files byte for byte. Alt text for each image is in `manifest.json`.
