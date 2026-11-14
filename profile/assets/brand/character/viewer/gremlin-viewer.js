// Drop-in gremlin: a poster image first, the animated model only when it is on screen,
// the device can take it and the visitor has not asked for less motion.
//
//   import { mountGremlin } from "./gremlin-viewer.js";
//   mountGremlin(document.querySelector("#gremlin"), { state: "idle" });
//
// The container holds an <img> poster (the same still the page already ships). The
// module adds a <canvas> over it and fades the poster out once the first frame is drawn.
// Nothing is fetched until the container is within `margin` of the viewport.
const here = new URL(".", import.meta.url);

export function canRun(nav = navigator, win = window) {
  const conn = nav.connection || {};
  if (conn.saveData || /(^|-)2g$/.test(conn.effectiveType || "")) return false;
  if (nav.deviceMemory && nav.deviceMemory < 4) return false;
  if (nav.hardwareConcurrency && nav.hardwareConcurrency < 4) return false;
  const gl = document.createElement("canvas").getContext("webgl2");
  if (!gl) return false;
  gl.getExtension("WEBGL_lose_context")?.loseContext();
  return typeof win.IntersectionObserver === "function" && typeof WebAssembly === "object";
}

// options: state, theme ("dark" | "light" | "auto"), src, margin, onError. Returns { destroy }.
export function mountGremlin(box, options = {}) {
  const opts = { state: "idle", theme: "auto", src: new URL("../gremlin.glb", here).href, margin: "200px", ...options };
  const still = matchMedia("(prefers-reduced-motion: reduce)");
  const lightMedia = matchMedia("(prefers-color-scheme: light)");
  const theme = () => (opts.theme === "auto" ? (lightMedia.matches ? "light" : "dark") : opts.theme);
  let canvas = null, scene = null, stopped = false, visible = false;

  const observer = new IntersectionObserver(async ([entry]) => {
    visible = entry.isIntersecting;
    if (!scene && visible) await start();
    else if (scene && !still.matches) visible ? scene.play() : scene.pause();
  }, { rootMargin: opts.margin });

  async function start() {
    if (scene || stopped || !canRun()) return;
    try {
      canvas = document.createElement("canvas");
      canvas.setAttribute("aria-hidden", "true");
      canvas.style.cssText = "position:absolute;inset:0;width:100%;height:100%;opacity:0;transition:opacity .25s";
      box.style.position ||= "relative";
      box.append(canvas);
      const { render } = await import("./gremlin-renderer.js");
      scene = await render(canvas, { src: opts.src, state: opts.state, theme: theme() });
      if (stopped) return scene.destroy();
      scene.draw();
      canvas.style.opacity = "1";
      if (!still.matches && visible) scene.play();
    } catch (error) {
      canvas?.remove();
      scene = null;
      (opts.onError || console.warn)(error);
    }
  }
  const retheme = () => { scene?.setTheme(theme()); scene?.draw(); };
  const calm = () => (still.matches ? scene?.pause() : visible && scene?.play());
  lightMedia.addEventListener("change", retheme);
  still.addEventListener("change", calm);
  observer.observe(box);
  return {
    setState: (name) => scene?.setState(name),
    destroy() {
      stopped = true;
      observer.disconnect();
      lightMedia.removeEventListener("change", retheme);
      still.removeEventListener("change", calm);
      scene?.destroy();
      canvas?.remove();
    },
  };
}
