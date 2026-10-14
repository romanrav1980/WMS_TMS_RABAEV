from pathlib import Path
s=Path("scripts/browser1334_forecast.mjs").read_text(encoding="utf-8");s=s[:s.index(" const before=")]
s+="""
 await page.locator('#wfLabourResult details').first().evaluate(el=>el.open=true);
 await page.locator('.wf-resources').screenshot({path:'reports/retailcase/2026-10-13/screenshots/87-ni081-forecast-hours.png'});
 console.log(JSON.stringify({text:await page.locator('#wfLabourResult').innerText(),errors}));
}finally{await browser.close();}
"""
Path("scripts/browser1340_forecast_screen.mjs").write_text(s,encoding="utf-8")
