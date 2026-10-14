(() => {
  function parts(value) {
    const text=String(value ?? "0");
    if(!/^(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)$/.test(text)||text.length>80)throw new Error("Invalid exact quantity");
    const [whole="",fraction=""]=text.split(".");
    return {whole:whole||"0",fraction};
  }
  function sum(rows,key) {
    try {
      const values=rows.map(row=>parts(row[key] ?? "0"));
      const scale=Math.max(0,...values.map(v=>v.fraction.length));
      const total=values.reduce((n,v)=>n+BigInt(v.whole+v.fraction.padEnd(scale,"0")),0n);
      const digits=total.toString().padStart(scale+1,"0");
      return scale?(digits.slice(0,-scale)+"."+digits.slice(-scale)).replace(/\.?0+$/,""):digits;
    } catch { return "—"; }
  }
  function display(value) {
    try {parts(value);return String(value ?? "0");} catch {return "—";}
  }
  window.caseQuantity={sum,display};
})();
