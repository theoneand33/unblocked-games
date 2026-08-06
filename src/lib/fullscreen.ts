// Fullscreen popup support shared by the flash pages and Run 3.
// ponytail: the run3 embed bootstrap is duplicated as a string inside
// buildPopupHtml because a popup is a fresh document with no module access;
// the live page reuses embedRun3() below.

declare global {
  interface Window {
    lime?: {
      embed: (
        name: string,
        containerId: string,
        width: number,
        height: number,
        options: object,
      ) => void;
    };
  }
}

export function buildPopupHtml(
  kind: "flash" | "html5",
  gamePath: string,
  title: string,
): string {
  if (kind === "html5") {
    return [
      "<!DOCTYPE html><html><head>",
      '<meta charset="utf-8"><title>' + title + "</title>",
      '<base href="/games/run3/">',
      "<style>html,body{margin:0;height:100%;background:#000}#openfl-content{position:fixed;inset:0}</style>",
      '</head><body><div id="openfl-content"></div>',
      '<script src="/games/run3/Run3.js"><' + "/script>",
      "<script>",
      "window.addEventListener('touchmove',function(e){e.preventDefault();},{passive:false});",
      "function ready(){",
      "var el=document.getElementById('openfl-content');",
      "if(el&&typeof lime!=='undefined'&&lime.embed){lime.embed('Run3','openfl-content',800,600,{parameters:{}});}",
      "else{setTimeout(ready,200);}",
      "}",
      "ready();",
      "<" + "/script>",
      "</body></html>",
    ].join("");
  }
  return [
    "<!DOCTYPE html><html><head>",
    '<meta charset="utf-8"><title>' + title + "</title>",
    "<style>html,body{margin:0;height:100%;overflow:hidden;background:#000}#wrap{position:fixed;inset:0}</style>",
    '</head><body><div id="wrap"></div>',
    '<script src="/ruffle/ruffle.js"><' + "/script>",
    "<script>",
    "function ready(){",
    "var wrap=document.getElementById('wrap');",
    "var r=window.RufflePlayer;",
    "var ruff=(r&&typeof r.newest==='function')?r.newest():null;",
    "if(wrap&&ruff&&typeof ruff.createPlayer==='function'){",
    "var p=ruff.createPlayer();",
    "p.style.width='100%';p.style.height='100%';",
    "wrap.appendChild(p);",
    "p.load('" + gamePath + "');",
    "}else{setTimeout(ready,200);}",
    "}",
    "ready();",
    "<" + "/script>",
    "</body></html>",
  ].join("");
}

// Opens the popup. A synthetic <a> click runs inside the user gesture, so
// popup blockers treat it like a normal tab open (window.open would not).
export function openFullscreen(
  kind: "flash" | "html5",
  gamePath: string,
  title: string,
): void {
  const blob = new Blob([buildPopupHtml(kind, gamePath, title)], {
    type: "text/html",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
  // ponytail: hold the blob URL alive long enough for the popup to load
  setTimeout(() => URL.revokeObjectURL(url), 60000);
}

// Run 3 embed bootstrap for the live page (touch guard + lime polling).
export function embedRun3(containerId: string): void {
  window.addEventListener("touchmove", (event) => event.preventDefault(), {
    passive: false,
  });

  const ready = (): void => {
    const el = document.getElementById(containerId);
    if (el && typeof window.lime !== "undefined" && window.lime.embed) {
      try {
        window.lime.embed("Run3", containerId, 800, 600, { parameters: {} });
      } catch (err) {
        console.error("Run3 embed failed:", err);
      }
    } else {
      setTimeout(ready, 200);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ready);
  } else {
    ready();
  }
}
