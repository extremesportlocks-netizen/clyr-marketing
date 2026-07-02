const puppeteer=require('puppeteer');
(async()=>{
const b=await puppeteer.launch({executablePath:'/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome',headless:'new',args:['--no-sandbox','--disable-dev-shm-usage']});
const TERMS=['UluRx','ulurx','Direct-Rx','DirectRx','CSN','C23504','Russ','MDI','provider queue','Karin','Tiffany','BondRx','DispensePro','Strive','Belmar','Olympia','Pharmacy Hub','Sonji'];
for(const cfg of [[1280,900,'d',false],[390,844,'m',true]]){
  const p=await b.newPage();
  await p.setViewport({width:cfg[0],height:cfg[1],deviceScaleFactor:1,isMobile:cfg[3]});
  await p.goto('https://www.clyr.health/ghk-cu-cream.html?cb='+Date.now(),{waitUntil:'networkidle2',timeout:45000});
  await new Promise(r=>setTimeout(r,1800));
  const res=await p.evaluate((terms)=>{
    const all=(document.documentElement.outerHTML||'');
    const txt=document.body.innerText||'';
    const hits={};
    for(const t of terms){
      const rx=new RegExp(t.replace(/[-\/\\^$*+?.()|[\]{}]/g,'\\$&'),'gi');
      const inHtml=(all.match(rx)||[]).length;
      const inText=(txt.match(rx)||[]).length;
      if(inHtml||inText) hits[t]={html:inHtml,text:inText};
    }
    return {hits, ov:document.documentElement.scrollWidth-document.documentElement.clientWidth, tierRows:document.querySelectorAll('.tier-row').length};
  },TERMS);
  console.log(cfg[2], JSON.stringify(res));
  await p.close();
}
await b.close();
})();
