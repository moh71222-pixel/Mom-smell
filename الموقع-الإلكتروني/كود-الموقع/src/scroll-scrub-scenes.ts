/**
 * Scene data for the Raihat Ummi journey: one continuous film (raw materials
 * swirl and roll into a ball of mamool), cut on exact frames into four
 * chapters so each chapter owns its own stretch of scroll.
 *
 * Every `poster` is the exact first frame of the encoded clip beside it.
 * Keep this array a module constant.
 */
import type {
  ScrollScrubScene,
  ScrollScrubTheme,
} from "@/components/scroll-scrub/scroll-scrub";

/** Brand tokens: Aja night teal, cream ink, Najdi ochre. */
export const scrollScrubTheme: ScrollScrubTheme = {
  accent: "#C99A3C",
  background: "#061F23",
  ink: "#F4ECDD",
  muted: "#D9C9AE",
};

const world = (n: string) => ({
  clip: `/assets/world/scene-${n}.mp4`,
  mobileClip: `/assets/world/scene-${n}-mobile.mp4`,
  mobilePoster: `/assets/world/scene-${n}-mobile-poster.jpg`,
  poster: `/assets/world/scene-${n}-poster.jpg`,
});

export const scrollScrubScenes: ScrollScrubScene[] = [
  {
    ...world("01"),
    body: "بودرة عود، زيت الخلطة، ظفر، جاوي ولبان. كل خامة ننتقيها بيدنا قبل لا تدخل العجنة.",
    id: "khamat",
    kicker: "رائحة أمي · من حائل",
    label: "الخامات",
    scroll: 1.4,
    tags: ["بودرة عود", "ظفر", "لبان"],
    title: "خمس خامات، وحبة وحدة",
  },
  {
    ...world("02"),
    align: "right",
    body: "قطرات الزيت تسقي البودرة، والظفر والجاوي يذوبون فيها على مهل حتى تصير الخلطة روح وحدة.",
    id: "khalta",
    kicker: "الخلطة",
    label: "الخلطة",
    scroll: 1.3,
    title: "تمتزج على مهل",
  },
  {
    ...world("03"),
    body: "نعجن ونكوّر كل حبة على طريقة البيوت الحايلية، بدون مكينة وبدون استعجال.",
    id: "takweer",
    kicker: "التكوير",
    label: "التكوير",
    scroll: 1.3,
    title: "تتكوّر بين الكفّين",
  },
  {
    ...world("04"),
    align: "right",
    body: "حبة دافية تفوح في بيتك مثل ما كانت تفوح في بيت أمي. هذا هو المعمول، وهذي بداية الحكاية.",
    id: "mamool",
    kicker: "المعمول",
    label: "المعمول",
    linger: 0.2,
    scroll: 1.5,
    title: "معمول رائحة أمي",
  },
];
