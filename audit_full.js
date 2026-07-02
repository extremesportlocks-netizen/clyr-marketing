const puppeteer=require('puppeteer');
(async()=>{
const b=await puppeteer.launch({executablePath:'/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome',headless:'new',args:['--no-sandbox','--disable-dev-shm-usage']});
const results={};
for(const cfg of [[1280,900,'d',false],[390,844,'m',true]]){
  const p=await b.newPage();
  const errs=[]; p.on('console',m=>{if(m.type()==='error')errs.push(m.text().slice(0,120))});
  const fails=[]; p.on('requestfailed',r=>fails.push(r.url().split('/').pop()));
  const resp404=[]; p.on('response',r=>{if(r.status()>=400)resp404.push(r.status()+' '+r.url().split('/').pop())});
  await p.setViewport({width:cfg[0],height:cfg[1],deviceScaleFactor:2,isMobile:cfg[3]});
  await p.goto('https://www.clyr.health/ghk-cu-cream.html?cb='+Date.now(),{waitUntil:'networkidle2',timeout:45000});
  await new Promise(r=>setTimeout(r,2200));
  const info=await p.evaluate(()=>{
    const ov=document.documentElement.scrollWidth-document.documentElement.clientWidth;
    const loaded=document.body.classList.contains('is-loaded')||!!document.querySelector('.ghk-page.is-loaded, body.is-loaded');
    const heroVisible=(()=>{const t=document.querySelector('.ghk-title'); if(!t)return 'no title'; return getComputedStyle(t).opacity;})();
    const tierRows=document.querySelectorAll('.tier-row').length;
    const imgs=[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src.split('/').pop());
    const links=[...document.querySelectorAll('a[href^="/"]')].map(a=>a.getAttribute('href'));
    return {ov,heroOpacity:heroVisible,tierRows,brokenImgs:imgs,internalLinks:[...new Set(links)].length};
  });
  results[cfg[2]]={...info,consoleErrs:errs.slice(0,4),netFails:fails.slice(0,4),http4xx:resp404.slice(0,5)};
  await p.screenshot({path:'/home/claude/restored_'+cfg[2]+'.png',clip:{x:0,y:0,width:cfg[0],height:cfg[1]}});
  await p.close();
}
console.log(JSON.stringify(results,null,1));
await b.close();
})();
