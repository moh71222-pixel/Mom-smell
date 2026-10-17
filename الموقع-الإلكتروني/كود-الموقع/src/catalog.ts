/** The Raihat Ummi product line: four families, twelve products. */
export interface Product {
  name: string;
  note: string;
  size: string;
  price: number;
  label: string;
}

export interface Family {
  id: string;
  title: string;
  lead: string;
  photo: string;
  photoAlt: string;
  products: Product[];
}

export const families: Family[] = [
  {
    id: "mamool",
    title: "المعمول",
    lead: "يُعجن ويُكوَّر باليد من بودرة العود وزيت الخلطة والظفر والجاوي واللبان.",
    photo: "/assets/products/mamool.webp",
    photoAlt: "برطمان زجاجي بغطاء ذهبي مليان حبات معمول",
    products: [
      { name: "الملكي", note: "خلطة البيت الأصيلة", size: "80 جرام", price: 130, label: "/assets/labels/mamool-malaki.svg" },
      { name: "المخصوص", note: "خلطة الدوسري", size: "100 جرام", price: 250, label: "/assets/labels/mamool-makhsoos.svg" },
      { name: "العرايسي", note: "لليالي الفرح", size: "80 جرام", price: 120, label: "/assets/labels/mamool-arayesi.svg" },
    ],
  },
  {
    id: "oud",
    title: "العود",
    lead: "قطع عود مختارة، تُسقى بالزيوت وتترك حتى تشرب الرائحة.",
    photo: "/assets/products/oud.webp",
    photoAlt: "قطع عود داكنة في مبخرة نجدية حمراء يتصاعد منها الدخان",
    products: [
      { name: "عود مسقى", note: "دخون يومي", size: "80 جرام", price: 95, label: "/assets/labels/oud-musqa.svg" },
      { name: "عود طبيعي", note: "مسقى زيوت", size: "80 جرام", price: 250, label: "/assets/labels/oud-tabiei.svg" },
    ],
  },
  {
    id: "sprays",
    title: "المرشات",
    lead: "للمجلس والمفارش والستاير. رشة وحدة تكفي تعطّر المكان.",
    photo: "/assets/products/spray.webp",
    photoAlt: "ثلاث قوارير مرش كريمية بأغطية ذهبية",
    products: [
      { name: "أسيل", note: "مرش مفارش ومجالس", size: "500 مل", price: 80, label: "/assets/labels/spray-aseel.svg" },
      { name: "شهد", note: "مرش مفارش ومجالس", size: "500 مل", price: 80, label: "/assets/labels/spray-shahd.svg" },
      { name: "سديم", note: "مرش مفارش ومجالس", size: "500 مل", price: 80, label: "/assets/labels/spray-sadeem.svg" },
    ],
  },
  {
    id: "oils",
    title: "الأدهان",
    lead: "أدهان مركزة بالتولة، تثبت على الجلد والثوب طول اليوم.",
    photo: "/assets/products/oil.webp",
    photoAlt: "قوارير دهن كريستال بأغطية ذهبية وخيوط زعفران",
    products: [
      { name: "فتشة العروس", note: "دهن عطري", size: "تولة", price: 70, label: "/assets/labels/oil-fitshat.svg" },
      { name: "خمرية الزعفران", note: "دهن عطري", size: "تولة", price: 60, label: "/assets/labels/oil-saffron.svg" },
      { name: "خمرية المسك", note: "دهن عطري", size: "تولة", price: 60, label: "/assets/labels/oil-musk.svg" },
      { name: "دهن العود الطبيعي", note: "دهن عود صافي", size: "ربع تولة", price: 120, label: "/assets/labels/oil-oud.svg" },
    ],
  },
];

export const links = {
  instagram: "https://www.instagram.com/mum_smell",
  tiktok: "https://www.tiktok.com/@mum_smell",
};
