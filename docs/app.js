// Scroll plays the film: the journey section's scroll progress maps to video time.
(() => {
  const journey = document.querySelector(".journey");
  const video = journey.querySelector(".journey__video");
  const routeLinks = [...journey.querySelectorAll(".journey__route a")];
  const chapters = [...journey.querySelectorAll(".chapter")];
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const small = matchMedia("(max-width: 860px), (pointer: coarse)").matches;

  let target = 0;
  let current = 0;
  let ready = false;

  const progress = () => {
    const rect = journey.getBoundingClientRect();
    const span = journey.offsetHeight - innerHeight;
    return span > 0 ? Math.min(1, Math.max(0, -rect.top / span)) : 0;
  };

  const onScroll = () => {
    const p = progress();
    journey.style.setProperty("--p", p.toFixed(4));
    if (ready) target = p * (video.duration - 0.05);
    const mid = innerHeight / 2;
    let active = 0;
    chapters.forEach((ch, i) => {
      if (ch.getBoundingClientRect().top < mid) active = i;
    });
    routeLinks.forEach((a, i) => a.classList.toggle("is-active", i === active));
  };

  const tick = () => {
    if (ready) {
      current += (target - current) * 0.18;
      if (Math.abs(video.currentTime - current) > 0.02 && !video.seeking) {
        video.currentTime = current;
      }
    }
    requestAnimationFrame(tick);
  };

  addEventListener("scroll", onScroll, { passive: true });
  addEventListener("resize", onScroll);
  onScroll();

  if (reduced) return; // the poster and the chapter copy tell the story on their own

  // Load the whole clip as a Blob so seeking never waits on the network.
  const src = small ? video.dataset.srcMobile : video.dataset.src;
  fetch(src)
    .then((r) => r.blob())
    .then((blob) => {
      video.src = URL.createObjectURL(blob);
      video.load();
    })
    .catch(() => {
      video.src = src;
    });

  video.addEventListener("loadeddata", () => {
    ready = true;
    journey.classList.add("is-ready");
    onScroll();
    current = target;
    video.currentTime = current;
  });

  // iOS needs one user gesture before a paused video will paint seeked frames.
  const prime = () => {
    video.play().then(() => video.pause()).catch(() => {});
    removeEventListener("touchstart", prime);
  };
  addEventListener("touchstart", prime, { passive: true });

  requestAnimationFrame(tick);
})();
