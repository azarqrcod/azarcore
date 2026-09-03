const translations={
  en:{
    navServices:"Services",navWork:"Projects",navContact:"Contact",navCta:"Start a project",
    heroKicker:"DIGITAL STUDIO · BERLIN",heroTitle:"A digital presence,<br><em>built to be remembered.</em>",heroLead:"We combine design, NFC technology and smart web solutions into an experience that looks professional and works effortlessly.",heroPrimary:"Request a free consultation",heroSecondary:"View projects",trustOne:"Direct contact",trustTwo:"Individual design",trustThree:"For iPhone & Android",floatOne:"CONTACT IN SECONDS",floatTwo:"SMART & DIRECT",
    proofTitle:"One touchpoint. Every important destination.",servicesKicker:"WHAT WE DO",servicesTitle:"Technology, design and brand.<br><em>From one studio.</em>",servicesLead:"No interchangeable templates. Every solution is designed around the business.",
    serviceOneTitle:"NFC Business Profile",serviceOneText:"One tap opens contacts, social media, location and offers — no app required.",serviceTwoTitle:"QR & Digital Menus",serviceTwoText:"Fast, easy-to-update menus and information pages for hospitality and retail.",serviceThreeTitle:"Web & Landing Pages",serviceThreeText:"Mobile websites with clear journeys, strong design and direct action.",serviceFourTitle:"Branding & AI Creative",serviceFourText:"Visual identities, logos and creative content for one consistent brand.",
    workKicker:"SELECTED PROJECTS",workTitle:"Not just promised.<br><em>Already delivered.</em>",workLead:"Digital profiles built to load quickly on mobile and guide customers directly to the right action.",openProject:"VIEW LIVE ↗",nfcCardTitle:"Smart Business Card",
    processKicker:"HOW IT WORKS",processTitle:"From idea to finished product.",stepOneTitle:"Brief",stepOneText:"You send your logo, contact details and required content.",stepTwoTitle:"Design",stepTwoText:"We create an individual mobile experience for your brand.",stepThreeTitle:"Activation",stepThreeText:"After approval, your link is activated on NFC or QR.",
    contactKicker:"YOUR NEXT PROJECT",contactTitle:"Ready for a presence<br><em>that feels professional?</em>",contactWhatsapp:"Discuss your project",footerText:"Digital · AI · Creative Solutions"
  },
  fa:{
    navServices:"خدمات",navWork:"نمونه‌کارها",navContact:"تماس",navCta:"شروع پروژه",
    heroKicker:"استودیوی دیجیتال · برلین",heroTitle:"حضور دیجیتالی،<br><em>که در ذهن می‌ماند.</em>",heroLead:"ما طراحی، فناوری NFC و راهکارهای هوشمند وب را ترکیب می‌کنیم تا برند شما حرفه‌ای دیده شود و ارتباط با مشتری ساده‌تر باشد.",heroPrimary:"درخواست مشاوره رایگان",heroSecondary:"مشاهده پروژه‌ها",trustOne:"ارتباط مستقیم",trustTwo:"طراحی اختصاصی",trustThree:"مناسب آیفون و اندروید",floatOne:"ارتباط در چند ثانیه",floatTwo:"هوشمند و مستقیم",
    proofTitle:"یک نقطه تماس؛ تمام مسیرهای مهم.",servicesKicker:"خدمات ما",servicesTitle:"فناوری، طراحی و برند؛<br><em>همه در یک مجموعه.</em>",servicesLead:"از قالب‌های تکراری استفاده نمی‌کنیم؛ هر پروژه متناسب با هویت همان کسب‌وکار طراحی می‌شود.",
    serviceOneTitle:"پروفایل تجاری NFC",serviceOneText:"با یک لمس، شماره تماس، شبکه‌های اجتماعی، آدرس و خدمات باز می‌شود؛ بدون نیاز به اپلیکیشن.",serviceTwoTitle:"QR و منوی دیجیتال",serviceTwoText:"منوها و صفحات اطلاعاتی سریع و قابل‌به‌روزرسانی برای کافه، رستوران و فروشگاه.",serviceThreeTitle:"وب‌سایت و لندینگ‌پیج",serviceThreeText:"وب‌سایت‌های موبایل‌محور با مسیر روشن، طراحی قوی و دسترسی مستقیم.",serviceFourTitle:"برندینگ و طراحی با هوش مصنوعی",serviceFourText:"هویت بصری، لوگو و محتوای خلاقانه برای ساخت یک برند یکپارچه.",
    workKicker:"پروژه‌های منتخب",workTitle:"فقط وعده نیست؛<br><em>پروژه‌های اجراشده.</em>",workLead:"پروفایل‌ها و صفحات دیجیتالی که روی موبایل سریع باز می‌شوند و مشتری را مستقیماً به اقدام موردنظر هدایت می‌کنند.",openProject:"مشاهده آنلاین ↗",nfcCardTitle:"کارت ویزیت هوشمند",
    processKicker:"مراحل انجام کار",processTitle:"از ایده تا محصول نهایی.",stepOneTitle:"دریافت اطلاعات",stepOneText:"لوگو، مشخصات تماس و محتوای موردنظر را ارسال می‌کنید.",stepTwoTitle:"طراحی اختصاصی",stepTwoText:"یک تجربه موبایلی متناسب با هویت برند شما طراحی می‌کنیم.",stepThreeTitle:"فعال‌سازی",stepThreeText:"پس از تأیید شما، لینک روی NFC یا QR فعال می‌شود.",
    contactKicker:"پروژه بعدی شما",contactTitle:"برای یک حضور دیجیتال<br><em>واقعاً حرفه‌ای آماده‌اید؟</em>",contactWhatsapp:"گفت‌وگو درباره پروژه",footerText:"راهکارهای دیجیتال · هوش مصنوعی · طراحی خلاق"
  }
};
let language="de";
const order=["de","en","fa"];
const toggle=document.getElementById("langToggle");
document.querySelectorAll("[data-i18n]").forEach(el=>el.dataset.de=el.innerHTML);
function applyLanguage(lang){
  language=lang;
  document.documentElement.lang=lang;
  document.documentElement.dir=lang==="fa"?"rtl":"ltr";
  const next=order[(order.indexOf(lang)+1)%order.length];
  toggle.textContent=next.toUpperCase();
  toggle.setAttribute("aria-label",next==="de"?"Auf Deutsch wechseln":next==="en"?"Switch to English":"تغییر زبان به فارسی");
  document.querySelectorAll("[data-i18n]").forEach(el=>{el.innerHTML=lang==="de"?el.dataset.de:translations[lang][el.dataset.i18n]});
}
toggle.addEventListener("click",()=>applyLanguage(order[(order.indexOf(language)+1)%order.length]));
const observer=new IntersectionObserver(entries=>entries.forEach(entry=>entry.isIntersecting&&entry.target.classList.add("visible")),{threshold:.12});
document.querySelectorAll(".service-card,.project,.steps li").forEach(el=>{el.classList.add("reveal");observer.observe(el)});
