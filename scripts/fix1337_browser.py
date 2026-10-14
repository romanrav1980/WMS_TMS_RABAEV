from pathlib import Path
p=Path("scripts/browser1334_forecast.mjs");s=p.read_text(encoding="utf-8")
s=s.replace(' const open=async()=>{',' let visit=0;const open=async()=>{')
s=s.replace("  await page.locator('#adminLoginForm button[type=submit]').click();","  if(visit++===0)await page.locator('#adminLoginForm button[type=submit]').click();")
s=s.replace("if(!before.includes('Вид работы не связан'))throw Error(before);","")
s=s.replace("  await route.abort('failed');","  fs.writeFileSync('tmp/committed1334.json',JSON.stringify({submitted,committed},null,2));\n  await route.abort('failed');")
p.write_text(s,encoding="utf-8")
