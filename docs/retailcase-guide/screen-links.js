/* One route mapping for screen help and links from role documents. */
(() => {
'use strict';
function url(target){
 if(target.startsWith('raw:'))return 'http://127.0.0.1:8088/wms-admin/'+target.slice(4);
 if(target.startsWith('store:'))return 'http://127.0.0.1:3010'+target.slice(6);
 return 'http://127.0.0.1:3000/?'+(target.startsWith('workspace=')?'page=workspace&':'')+target;
}
window.GuideScreenLinks={url};
})();
