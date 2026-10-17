import { createFileRoute } from "@tanstack/react-router";

import { ScrollScrub } from "@/components/scroll-scrub/scroll-scrub";
import { families, links } from "@/catalog";
import { scrollScrubScenes, scrollScrubTheme } from "@/scroll-scrub-scenes";

export const Route = createFileRoute("/")({
  component: Index,
});

// Module constant: the last chapter gets its own CTA without changing the
// array identity between renders.
const scenes = scrollScrubScenes.map((scene, index) =>
  index === scrollScrubScenes.length - 1
    ? {
        ...scene,
        actions: (
          <a className="ru-seal-cta" href="#collection">
            <span className="ru-seal-cta__ring" aria-hidden="true" />
            <span>شوف المجموعة</span>
          </a>
        ),
      }
    : scene,
);

const price = (value: number) => `${value} ر.س`;

function Index() {
  return (
    <div className="ru" dir="rtl" lang="ar">
      <SiteHeader />
      <main>
        <ScrollScrub className="ru-journey" scenes={scenes} theme={scrollScrubTheme} />
        <Collection />
        <Story />
        <Order />
      </main>
      <SiteFooter />
    </div>
  );
}

function SiteHeader() {
  return (
    <header className="ru-header">
      <a className="ru-header__brand" href="#khamat" aria-label="رائحة أمي">
        <img src="/assets/brand/mark.svg" alt="" width={44} height={44} />
        <span className="ru-header__name">رائحة أمي</span>
      </a>
      <nav className="ru-header__nav" aria-label="أقسام الموقع">
        <a href="#collection">المجموعة</a>
        <a href="#story">حكايتنا</a>
        <a href="#order">الطلب</a>
      </nav>
      <a className="ru-header__order" href={links.instagram} target="_blank" rel="noreferrer">
        اطلب الحين
      </a>
    </header>
  );
}

function Collection() {
  return (
    <section className="ru-collection" id="collection" aria-labelledby="collection-title">
      <div className="ru-ribbon" aria-hidden="true" />
      <div className="ru-collection__intro">
        <h2 className="ru-display" id="collection-title">
          المجموعة
        </h2>
        <p>أربع عائلات، كل وحدة لها طقسها في البيت. الأسعار بالريال السعودي.</p>
        <ul className="ru-collection__jump">
          {families.map((family) => (
            <li key={family.id}>
              <a href={`#${family.id}`}>{family.title}</a>
            </li>
          ))}
        </ul>
      </div>

      {families.map((family, index) => (
        <article
          className="ru-family"
          data-flip={index % 2 === 1 ? "true" : undefined}
          id={family.id}
          key={family.id}
        >
          <figure className="ru-family__photo">
            <img src={family.photo} alt={family.photoAlt} loading="lazy" width={960} height={1200} />
            <figcaption>
              <span className="ru-family__index">0{index + 1}</span>
              {family.title}
            </figcaption>
          </figure>

          <div className="ru-family__body">
            <h3 className="ru-family__title">{family.title}</h3>
            <p className="ru-family__lead">{family.lead}</p>
            <ul className="ru-family__list">
              {family.products.map((product) => (
                <li className="ru-product" key={product.name}>
                  <div className="ru-product__label">
                    <img src={product.label} alt={`ملصق ${product.name}`} loading="lazy" />
                  </div>
                  <div className="ru-product__text">
                    <p className="ru-product__name">{product.name}</p>
                    <p className="ru-product__note">
                      {product.note} · {product.size}
                    </p>
                  </div>
                  <p className="ru-product__price">{price(product.price)}</p>
                  <a
                    className="ru-product__ask"
                    href={links.instagram}
                    target="_blank"
                    rel="noreferrer"
                    aria-label={`اطلب ${product.name}`}
                  >
                    اطلب
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </article>
      ))}
    </section>
  );
}

function Story() {
  return (
    <section className="ru-story" id="story" aria-labelledby="story-title">
      <figure className="ru-story__band">
        <img src="/assets/story/crop_aja.jpg" alt="جبال أجا وسلمى في حائل" loading="lazy" />
      </figure>
      <div className="ru-story__grid">
        <div className="ru-story__mark">
          <img src="/assets/brand/logo-door-rev.svg" alt="شعار الباب النجدي لرائحة أمي" loading="lazy" />
        </div>
        <div className="ru-story__copy">
          <h2 className="ru-display" id="story-title">
            من حائل، من بيت أمي
          </h2>
          <p>
            بدأت رائحة أمي من مبخرة في مجلس حايلي، ومن وصفة معمول تتوارثها البيوت. أخذنا ألوان جبال أجا
            وسلمى، ومثلثات الأبواب النجدية، ودفء الطين، وصنعنا منها هوية تشبه المكان اللي جينا منه.
          </p>
          <dl className="ru-facts">
            <div>
              <dt>يدوي</dt>
              <dd>كل حبة معمول تتكوّر باليد</dd>
            </div>
            <div>
              <dt>حائلي</dt>
              <dd>خلطات البيوت الأصيلة</dd>
            </div>
            <div>
              <dt>مختار</dt>
              <dd>خامات ننتقيها بنفسنا</dd>
            </div>
          </dl>
        </div>
      </div>
    </section>
  );
}

function Order() {
  return (
    <section className="ru-order" id="order" aria-labelledby="order-title">
      <div className="ru-ribbon" aria-hidden="true" />
      <h2 className="ru-display" id="order-title">
        كيف تطلب
      </h2>
      <ol className="ru-steps">
        <li>
          <span className="ru-steps__n" aria-hidden="true">١</span>
          <p className="ru-steps__t">اختر من المجموعة</p>
          <p>المعمول، العود، المرشات أو الأدهان.</p>
        </li>
        <li>
          <span className="ru-steps__n" aria-hidden="true">٢</span>
          <p className="ru-steps__t">راسلنا</p>
          <p>على انستقرام أو تيك توك باسم المنتج والكمية.</p>
        </li>
        <li>
          <span className="ru-steps__n" aria-hidden="true">٣</span>
          <p className="ru-steps__t">يوصلك مغلّف</p>
          <p>بعلبة رائحة أمي وختمها، جاهز للهدية.</p>
        </li>
      </ol>
      <div className="ru-order__ctas">
        <a className="ru-cta-insta" href={links.instagram} target="_blank" rel="noreferrer">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" strokeWidth="2" />
            <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" strokeWidth="2" />
            <circle cx="17.5" cy="6.5" r="1.3" fill="currentColor" />
          </svg>
          راسلنا على انستقرام
        </a>
        <a className="ru-cta-tiktok" href={links.tiktok} target="_blank" rel="noreferrer">
          تابعنا على تيك توك
          <span aria-hidden="true">@mum_smell</span>
        </a>
      </div>
    </section>
  );
}

function SiteFooter() {
  return (
    <footer className="ru-footer">
      <img src="/assets/brand/logo-square-rev.svg" alt="رائحة أمي Raihat Ummi" loading="lazy" />
      <p>رائحة أمي · Raihat Ummi</p>
      <p className="ru-footer__small">صُنع يدوياً في حائل · ٢٠٢٦</p>
    </footer>
  );
}
