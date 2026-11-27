(()=>{const ser=new URLSearchParams(location.search).get('series_ticker');const j=JSON.parse(document.body.innerText);
const D=['26NOV29','26NOV30'];const c=x=>x==null||x===''?'':Math.round(parseFloat(x)*100);
const ms=(j.markets||[]).filter(m=>D.some(d=>m.event_ticker.includes(d)));
const GAMES=['KXNFLGAME','KXNFLSPREAD','KXNFLTOTAL','KXNFLTEAMTOTAL','KXNFLTEAMSACK'];
const q=m=>c(m.yes_ask_dollars)+'/'+c(m.yes_bid_dollars)+'/'+c(m.no_ask_dollars);
let out=new Date().toISOString()+' '+ser+' n='+ms.length+' all='+(j.markets||[]).length+' cursor='+(j.cursor||'')+' pages=1'+(GAMES.includes(ser)&&ser!=='KXNFLGAME'?' grouped':'')+'\n';
const g={},names={};
for(const m of ms){const p=m.ticker.split('-');const code=p[1].slice(7);const tr=m.status==='active'?1:0;
 if(ser==='KXNFLGAME'){(g[code+'|'+p[2]]=g[code+'|'+p[2]]||[]).push(q(m)+'|'+tr);continue}
 if(GAMES.includes(ser)){const s=p[2];let team,k;if(ser==='KXNFLTOTAL'){team='T';k=s}else{const mm=s.match(/^([A-Z]+?)(\d+)$/);team=mm?mm[1]:s;k=mm?mm[2]:''}
  (g[code+'|'+team]=g[code+'|'+team]||[]).push(k+':'+q(m)+':'+tr);continue}
 const pc=p[2],k=p[3];names[pc]=(m.title||'').split(':')[0].trim();(g[code+'|'+pc]=g[code+'|'+pc]||[]).push(k+':'+q(m));}
const body=Object.entries(g).map(([a,b])=>ser==='KXNFLGAME'?a+'|'+b[0]:a+'|'+b.join(',')).join(';');
out+=body;if(Object.keys(names).length)out+='\n#\n'+Object.entries(names).map(([a,b])=>a+'='+b).join(';');
localStorage.setItem('wz12s_'+ser,out);
return {ser,n:ms.length,all:(j.markets||[]).length,cursor:j.cursor||'',ev:[...new Set(ms.map(m=>m.event_ticker.split('-')[1]))].length,sample:ms[0]&&{t:ms[0].ticker,ti:ms[0].title}};})()
