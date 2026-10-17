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

// Order basket: products are added from the collection; "send" copies a ready
// order message and opens an Instagram chat with the shop.
(() => {
  const KEY = "raihat-cart";
  const DM = "https://ig.me/m/mum_smell";
  const root = document.documentElement;
  const cart = document.querySelector("[data-cart]");
  const list = cart.querySelector("[data-cart-list]");
  const empty = cart.querySelector("[data-cart-empty]");
  const totalEl = cart.querySelector("[data-cart-total]");
  const send = cart.querySelector("[data-cart-send]");
  const counts = [...document.querySelectorAll("[data-count]")];
  const toast = document.querySelector("[data-toast]");
  let items = [];
  try { items = JSON.parse(localStorage.getItem(KEY)) || []; } catch { items = []; }

  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(items)); } catch {} };
  const sar = (n) => `${n} ر.س`;
  const total = () => items.reduce((s, i) => s + i.price * i.qty, 0);

  const say = (text) => {
    toast.textContent = text;
    toast.classList.add("is-on");
    clearTimeout(say.t);
    say.t = setTimeout(() => toast.classList.remove("is-on"), 2600);
  };

  const render = () => {
    const n = items.reduce((s, i) => s + i.qty, 0);
    counts.forEach((c) => {
      c.textContent = n;
      c.classList.remove("is-bump");
      void c.offsetWidth;
      c.classList.add("is-bump");
    });
    root.classList.toggle("has-items", n > 0);
    list.innerHTML = "";
    items.forEach((it, idx) => {
      const li = document.createElement("li");
      li.className = "cart__item";
      li.innerHTML = `
        <p class="cart__name"></p>
        <div class="cart__line"><span class="cart__price"></span>
          <span class="qty"><button type="button" data-inc aria-label="زيادة">+</button><span></span><button type="button" data-dec aria-label="إنقاص">−</button></span>
        </div>
        <p class="cart__meta"></p>`;
      li.querySelector(".cart__name").textContent = it.name;
      li.querySelector(".cart__meta").textContent = `${it.size} · ${sar(it.price)} للحبة`;
      li.querySelector(".cart__price").textContent = sar(it.price * it.qty);
      li.querySelector(".qty span").textContent = it.qty;
      li.querySelector("[data-inc]").onclick = () => { it.qty += 1; save(); render(); };
      li.querySelector("[data-dec]").onclick = () => {
        it.qty -= 1;
        if (it.qty <= 0) items.splice(idx, 1);
        save(); render();
      };
      list.appendChild(li);
    });
    empty.hidden = items.length > 0;
    totalEl.textContent = sar(total());
    send.setAttribute("aria-disabled", String(items.length === 0));
  };

  const open = () => { cart.hidden = false; cart.querySelector(".cart__close").focus(); };
  const close = () => { cart.hidden = true; };

  document.querySelectorAll("[data-add]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const { name, size } = btn.dataset;
      const price = Number(btn.dataset.price);
      const found = items.find((i) => i.name === name);
      if (found) found.qty += 1; else items.push({ name, size, price, qty: 1 });
      save(); render();
      btn.classList.add("is-added");
      setTimeout(() => btn.classList.remove("is-added"), 600);
      say(`انضاف ${name} لسلتك`);
    });
  });
  document.querySelectorAll("[data-cart-open]").forEach((b) => b.addEventListener("click", open));
  cart.querySelectorAll("[data-cart-close]").forEach((b) => b.addEventListener("click", close));
  addEventListener("keydown", (e) => { if (e.key === "Escape" && !cart.hidden) close(); });

  // A real link, so the browser never treats opening the chat as a pop-up.
  // The copy starts inside the same tap, before the new tab takes focus.
  send.addEventListener("click", (e) => {
    if (!items.length) { e.preventDefault(); return; }
    const lines = items.map((i) => `- ${i.name} (${i.size}) × ${i.qty} = ${sar(i.price * i.qty)}`);
    const text = `السلام عليكم، أبي أطلب من رائحة أمي:\n${lines.join("\n")}\nالمجموع: ${sar(total())}`;
    try {
      navigator.clipboard.writeText(text).then(
        () => say("نسخنا طلبك، الصقه في المحادثة وأرسله"),
        () => say("افتح المحادثة واكتب طلبك"));
    } catch { say("افتح المحادثة واكتب طلبك"); }
  });

  render();
})();

// Sections ease in as they scroll into view.
(() => {
  const els = document.querySelectorAll(".family, .ritual, .steps li, .story__grid, .collection__intro");
  if (!("IntersectionObserver" in window)) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -10% 0px" });
  els.forEach((el) => { el.classList.add("reveal"); io.observe(el); });
})();
