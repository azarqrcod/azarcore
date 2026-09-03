const translations={
  en:{
    navServices:"Services",navWork:"Projects",navContact:"Contact",navCta:"Start a project",
    heroKicker:"DIGITAL STUDIO · BERLIN",heroTitle:"A digital presence,<br><em>built to be remembered.</em>",heroLead:"We combine design, NFC technology and smart web solutions into an experience that looks professional and works effortlessly.",heroPrimary:"Request a free consultation",heroSecondary:"View projects",trustOne:"Direct contact",trustTwo:"Individual design",trustThree:"For iPhone & Android",floatOne:"CONTACT IN SECONDS",floatTwo:"SMART & DIRECT",
    proofTitle:"One touchpoint. Every important destination.",servicesKicker:"WHAT WE DO",servicesTitle:"Technology, design and brand.<br><em>From one studio.</em>",servicesLead:"No interchangeable templates. Every solution is designed around the business.",
    serviceOneTitle:"NFC Business Profile",serviceOneText:"One tap opens contacts, social media, location and offers — no app required.",serviceTwoTitle:"QR & Digital Menus",serviceTwoText:"Fast, easy-to-update menus and information pages for hospitality and retail.",serviceThreeTitle:"Web & Landing Pages",serviceThreeText:"Mobile websites with clear journeys, strong design and direct action.",serviceFourTitle:"Branding & AI Creative",serviceFourText:"Visual identities, logos and creative content for one consistent brand.",
    workKicker:"SELECTED PROJECTS",workTitle:"Not just promised.<br><em>Already delivered.</em>",workLead:"Digital profiles built to load quickly on mobile and guide customers directly to the right action.",openProject:"VIEW LIVE ↗",nfcCardTitle:"Smart Business Card",
    processKicker:"HOW IT WORKS",processTitle:"From idea to finished product.",stepOneTitle:"Brief",stepOneText:"You send your logo, contact details and required content.",stepTwoTitle:"Design",stepTwoText:"We create an individual mobile experience for your brand.",stepThreeTitle:"Activation",stepThreeText:"After approval, your link is activated on NFC or QR.",
    contactKicker:"YOUR NEXT PROJECT",contactTitle:"Ready for a presence<br><em>that feels professional?</em>",footerText:"Digital · AI · Creative Solutions"
  }
};
let language="de";
const toggle=document.getElementById("langToggle");
toggle.addEventListener("click",()=>{
  language=language==="de"?"en":"de";
  document.documentElement.lang=language;
  toggle.textContent=language==="de"?"EN":"DE";
  toggle.setAttribute("aria-label",language==="de"?"Switch to English":"Auf Deutsch wechseln");
  document.querySelectorAll("[data-i18n]").forEach(el=>{
    if(!el.dataset.de)el.dataset.de=el.innerHTML;
    el.innerHTML=language==="en"?translations.en[el.dataset.i18n]:el.dataset.de;
  });
});
const observer=new IntersectionObserver(entries=>entries.forEach(entry=>entry.isIntersecting&&entry.target.classList.add("visible")),{threshold:.12});
document.querySelectorAll(".service-card,.project,.steps li").forEach(el=>{el.classList.add("reveal");observer.observe(el)});
