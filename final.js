const puppeteer=require('puppeteer');
(async()=>{
const b=await puppeteer.launch({executablePath:'/home/claude/.cache/puppeteer/chrome/linux-131.0.6778.204/chrome-linux64/chrome',headless:'new',args:['--no-sandbox','--disable-dev-shm-usage']});
for(const[vw,vh,tag,mob] of [[1280,900,'d',false],[390,844,'m',true]]){
  const p=await b.newPage();
  await p.setViewport({width:vw,height:vh,deviceScaleFactor:2,isMobile:mob});
  await p.goto('https://www.clyr.health/ghk-cu-cream.html?cb='+Date.now(),{waitUntil:'networkidle2',timeout:45000});
  await new Promise(r=>setTimeout(r,1500));
  const ov=await p.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  console.log(tag,'overflow:',ov);
  await p.screenshot({path:`/home/claude/fin_${tag}.png`,clip:{x:0,y:0,width:vw,height:vh}});
  await p.close();
}
await b.close();
