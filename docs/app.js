// Opening film: plays by itself when the page opens, then the collection appears
// and the page can be browsed. Without JS (or with reduced motion) the page
// simply starts on the collection.
(() => {
  const root = document.documentElement;
  const intro = document.querySelector(".intro");
  const video = intro.querySelector(".intro__video");
  const captions = [...intro.querySelectorAll(".caption")];
  const bar = intro.querySelector(".intro__bar");
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = matchMedia("(max-width: 860px), (pointer: coarse)").matches;
  let done = false;
  let watchdog = 0;

  const finish = () => {
    if (done) return;
    done = true;
    clearTimeout(watchdog);
    video.pause();
    root.classList.remove("intro-playing");
    root.classList.add("intro-done");
  };

  const start = () => {
    done = false;
    root.classList.remove("intro-done");
    root.classList.add("intro-playing");
    scrollTo(0, 0);
    video.currentTime = 0;
    // If the film cannot start within a few seconds, go straight to the collection.
    watchdog = setTimeout(() => { if (video.currentTime < 0.1) finish(); }, 6000);
    video.play().catch(finish);
  };

  video.addEventListener("timeupdate", () => {
    const d = video.duration || 15;
    const t = video.currentTime / d;
    bar.style.setProperty("--t", t.toFixed(4));
    const active = Math.min(captions.length - 1, Math.floor(t * captions.length));
    captions.forEach((c, i) => c.classList.toggle("is-on", i === active));
    if (video.duration && video.currentTime >= video.duration - 0.12) finish();
  });
  video.addEventListener("ended", finish);
  video.addEventListener("error", finish);
  intro.querySelector(".intro__skip").addEventListener("click", finish);
  intro.querySelector(".replay").addEventListener("click", start);
  addEventListener("keydown", (e) => { if (e.key === "Escape" && !done) finish(); });

  if (reduced) {
    root.classList.add("intro-done");
    return;
  }
  video.src = small ? video.dataset.srcMobile : video.dataset.src;
  start();
})();
