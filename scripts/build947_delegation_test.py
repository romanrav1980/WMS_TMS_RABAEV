from pathlib import Path
import json
t=Path("scripts/check917_receiving_selection.cjs").read_text(encoding="utf-8")
t=t.replace("addEventListener(type,fn){this.handlers[type]=fn;},appendChild(n){this.children.push(n);return n;}","addEventListener(type,fn){this.handlers[type]=fn;},appendChild(n){n.parent=this;this.children.push(n);return n;},contains(n){return n===this||this.children.some(child=>child.contains(n));},closest(){return this.dataset.receiptSelectable?this:this.parent?.closest();}")
t=t.replace("replaceChildren(...list){this.children=list;}","replaceChildren(...list){this.children=list;for(const n of list)n.parent=this;}")
t=t.replace("button.handlers.click({stopPropagation(){}});","node('receiptLines').handlers.click({type:'click',target:button});")
t=t.replace("node('receiptLines').children[1].handlers.keydown({key:'Enter',preventDefault(){}});","node('receiptLines').handlers.keydown({type:'keydown',target:node('receiptLines').children[1],key:'Enter',preventDefault(){}});")
t=t.replace("917 PASS manual button/keyboard line selection","947 PASS delegated button/keyboard selection/current source line")
print(json.dumps({"scripts/check947_receiving_delegation.cjs":t},ensure_ascii=True))
