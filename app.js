// One common screen filter includes boot text, status bars and the flat photo canvas.
const mapCanvas=document.createElement('canvas');mapCanvas.width=128;mapCanvas.height=128;
const mapContext=mapCanvas.getContext('2d'),mapPixels=mapContext.createImageData(128,128);
for(let y=0;y<128;y++)for(let x=0;x<128;x++){const u=x/127*2-1,v=y/127*2-1,i=(y*128+x)*4;mapPixels.data[i]=128-100*u*(1-v*v);mapPixels.data[i+1]=128-100*v*(1-u*u);mapPixels.data[i+2]=128;mapPixels.data[i+3]=255;}
mapContext.putImageData(mapPixels,0,0);document.getElementById('curve-map').setAttribute('href',mapCanvas.toDataURL());
import {dimensions,toAscii} from './ascii.js';
const $=id=>document.getElementById(id);
const FONT='16px monospace';
const measure=document.createElement('canvas').getContext('2d');measure.font=FONT;
const advance=measure.measureText('M').width;
let sessionPower=false;
let devices=[],deviceId='',actualFacing='',switchAvailable=true;
let selectedFacing='user', mirrored=true, cameraLabel='FRONT REQUESTED / FACING UNREPORTED';
let geometry=null, animation=null, lastFrame=-Infinity;
const flat=document.createElement('canvas');
function drawText(){flat.width=Math.ceil(geometry.width);flat.height=Math.ceil(geometry.height);const x=flat.getContext('2d');x.fillStyle='#08160f';x.fillRect(0,0,flat.width,flat.height);x.fillStyle='#b4f5b0';x.font=FONT;const m=x.measureText('Mg'),baseline=(geometry.lineHeight+m.actualBoundingBoxAscent-m.actualBoundingBoxDescent)/2;$('ascii').textContent.split('\n').forEach((line,i)=>x.fillText(line,0,baseline+i*geometry.lineHeight));}
const sample=document.createElement('canvas');
const sampleContext=sample.getContext('2d',{willReadFrequently:true});
function live(now){animation=null;if(!['preview'].includes(state))return;try{if(now-lastFrame>=55&&$('video').readyState>=2){lastFrame=now;render($('video'));}}catch{fail('Live preview interrupted. Start again or retry with Camera power.');return;}animation=requestAnimationFrame(live);}

let state='idle', epoch=0, stream=null,  image=null, demo=false;
const stopTracks=s=>s?.getTracks().forEach(t=>t.stop());
function cleanup(){cancelAnimationFrame(animation);animation=null;lastFrame=-Infinity;const s=stream;stream=null;stopTracks(s);$('video').srcObject=null;}
function show(next,message){state=next;$('status').textContent=message;
 const active=sessionPower;
 $('power').setAttribute('aria-checked',String(sessionPower));
 $('switch').title=switchAvailable?'Request another camera':'Only one camera detected';
 $('physical-led').dataset.state=state==='result'?'captured':stream?'live':'off';$('physical-led').setAttribute('aria-label',state==='result'?'Snapshot frozen; camera active':stream?'Camera live':'Camera off');
 $('lamp').textContent=stream?'● CAMERA ACTIVE':'● CAMERA OFF';
 for(const [id,visible] of Object.entries({copy:['preview','result'].includes(state),switch:state==='preview',capture:state==='preview',save:state==='result','density-box':['preview','result'].includes(state),viewfinder:['preview','result'].includes(state),video:false,ascii:['preview','result'].includes(state),welcome:!['preview','result'].includes(state)}))$(id).hidden=!visible;
 for(const id of ['capture','switch','copy','save','density']){$(id).hidden=false;$(id).disabled=false;}
 $('density-box').hidden=false;
 $('source').textContent=state==='result'?(demo?'PROCEDURAL DEMO / NOT A PHOTO':`YOUR SNAPSHOT / ${mirrored?'MIRRORED':'UNMIRRORED'}`):active?`LIVE ASCII / ${cameraLabel} / ${mirrored?'MIRRORED':'UNMIRRORED'}`:'NO IMAGE LOADED';
}
function reset(message='Session closed. Image cleared.'){sessionPower=false;epoch++;cleanup();image=null;$('ascii').textContent='';show('idle',message);}
function fail(message){sessionPower=false;epoch++;cleanup();image=null;show('error',message);}
async function start(requested=selectedFacing,switching=false){if(!['idle','error','result',...(switching?['preview']:[])].includes(state))return;const previous=selectedFacing,previousId=deviceId,previousActual=actualFacing,previousMirror=mirrored;const alternative=devices.find(d=>d.deviceId&&d.deviceId!==previousId);reset();const token=++epoch;sessionPower=true;show('requesting','Waiting for camera permission. Close cancels this request.');
 try{if(!window.isSecureContext)throw new Error('insecure');if(!navigator.mediaDevices?.getUserMedia)throw new Error('unsupported');
 const request=(facing,id)=>navigator.mediaDevices.getUserMedia({video:{...(id?{deviceId:{exact:id}}:{facingMode:{ideal:facing}}),width:{ideal:960},height:{ideal:720}},audio:false});
 let incoming,recovered=false;
 try{incoming=await request(requested,switching?alternative?.deviceId:undefined);}catch(e){if(!switching||token!==epoch||e.name==='NotAllowedError')throw e;incoming=await request(previous,previousId||undefined);recovered=true;}
 if(token!==epoch){stopTracks(incoming);return;}
 const settings=incoming.getVideoTracks()[0]?.getSettings?.()||{};
 const actual=settings.facingMode,newId=settings.deviceId||'';
 const sameDevice=!!(previousId&&newId&&previousId===newId);
 const verified=switching&&!recovered&&!sameDevice&&((previousId&&newId&&newId!==previousId)||(!previousId&&actual&&previousActual&&actual!==previousActual));
 if(!switching||verified){
 actualFacing=actual||'';deviceId=newId;
 if(actual==='environment'||actual==='user'){selectedFacing=actual;mirrored=actual==='user';}
 cameraLabel=actual==='environment'?'REAR':actual==='user'?'FRONT':'CAMERA / FACING UNREPORTED';
 }else{selectedFacing=previous;deviceId=newId||previousId;actualFacing=previousActual;mirrored=previousMirror;}
 try{devices=(await navigator.mediaDevices.enumerateDevices()).filter(d=>d.kind==='videoinput');}catch{devices=[];}
 if(token!==epoch){stopTracks(incoming);return;}
 switchAvailable=devices.length!==1;
 const feedback=recovered?'Switch unavailable. Previous camera restored. ':switching&&!verified?'Switch unavailable or cannot be verified; orientation unchanged. ':switching?'Different camera verified. ':devices.length===1?'Only one camera detected; switching is disabled. ':'';
 if(token!==epoch){stopTracks(incoming);return;}stream=incoming;show('requesting','Camera connected. Preparing your preview — Close stops the camera.');
 stream.getVideoTracks().forEach(t=>t.addEventListener('ended',()=>{if(token===epoch)fail('Camera interrupted. Start again or retry with Camera power.');},{once:true}));
 $('video').srcObject=stream;await $('video').play();if(token!==epoch)return;
 frame($('video').videoWidth,$('video').videoHeight);show('preview',`${feedback}Live ASCII targets 18 FPS. Take a photo to freeze it; Stop releases the camera.`);render($('video'));animation=requestAnimationFrame(live);
 }catch(e){if(token!==epoch)return;const messages={NotAllowedError:'Camera permission denied. Allow access in browser settings or retry with Camera power.',NotFoundError:'No camera found. Connect one or retry with Camera power.',NotReadableError:'Camera busy or unavailable. Close other camera apps and retry.',insecure:'Camera needs localhost or HTTPS. Use Run.command.',unsupported:'Camera API unavailable. Use a supported browser or retry with Camera power.'};fail(messages[e.name]||messages[e.message]||'Camera could not start. Retry or retry with Camera power.');}}
function frame(width,height){const stage=$('stage');const w=Math.min(stage.clientWidth,stage.clientHeight*width/height);$('viewfinder').style.width=`${w}px`;$('viewfinder').style.height=`${w*height/width}px`;}
function render(source=image){if(!source)return;const w=source.videoWidth||source.width,h=source.videoHeight||source.height;if(!w||!h)return;const {columns,rows}=dimensions(w,h,$('density').value,advance/20);geometry={columns,rows,width:columns*advance,height:columns*advance*h/w};geometry.lineHeight=geometry.height/rows;if(sample.width!==columns||sample.height!==rows){sample.width=columns;sample.height=rows;}sampleContext.setTransform(1,0,0,1,0,0);sampleContext.clearRect(0,0,columns,rows);if(source===$('video')&&mirrored)sampleContext.setTransform(-1,0,0,1,columns,0);sampleContext.drawImage(source,0,0,columns,rows);$('ascii').textContent=toAscii(sampleContext.getImageData(0,0,columns,rows).data,columns,rows);$('density-value').textContent=`${columns} columns`;syncDial();drawText();fit();}
function fit(){if(!['preview','result'].includes(state)||!geometry)return;const source=state==='result'?image:$('video');frame(source.videoWidth||source.width,source.videoHeight||source.height);const scale=$('viewfinder').clientWidth/geometry.width;const pre=$('ascii');pre.style.font=FONT;pre.style.lineHeight=`${geometry.lineHeight}px`;pre.style.width=`${geometry.width}px`;pre.style.height=`${geometry.height}px`;pre.style.transform=`scale(${scale})`;const c=$('crt');c.width=Math.max(1,Math.round($('viewfinder').clientWidth));c.height=Math.max(1,Math.round($('viewfinder').clientHeight));c.getContext('2d').drawImage(flat,0,0,c.width,c.height);}
function result(c,isDemo){image=c;demo=isDemo;cancelAnimationFrame(animation);animation=null;show('result',isDemo?'Demo portrait generated locally. No camera was accessed.':'Frozen. Camera remains active; Capture resumes live. Copy or save this frame.');render();}
function unavailable(){ $('status').textContent=['idle','error'].includes(state)?'Turn on camera power first.':state==='requesting'?'Waiting for camera permission. Use Camera power to cancel.':'Live camera required for this action. Press Capture to resume live.';}
function capture(){if(state==='result'&&sessionPower&&stream){image=null;show('preview','Live ASCII targets 18 FPS. Capture freezes the current frame.');render($('video'));lastFrame=-Infinity;cancelAnimationFrame(animation);animation=requestAnimationFrame(live);return;}if(state!=='preview'){unavailable();return;}const v=$('video');if(v.readyState<2||!v.videoWidth){$('status').textContent='Camera is warming up. Please try again.';return;}try{const c=document.createElement('canvas');c.width=v.videoWidth;c.height=v.videoHeight;const ctx=c.getContext('2d');if(mirrored){ctx.translate(c.width,0);ctx.scale(-1,1);}ctx.drawImage(v,0,0);result(c,false);}catch{fail('No camera frame available. Please retry.');}}
function makeDemo(){reset();const c=document.createElement('canvas');c.width=640;c.height=480;const x=c.getContext('2d');const g=x.createRadialGradient(320,220,20,320,240,370);g.addColorStop(0,'#64735e');g.addColorStop(1,'#080e0a');x.fillStyle=g;x.fillRect(0,0,640,480);const oval=(cx,cy,rx,ry,color)=>{x.fillStyle=color;x.beginPath();x.ellipse(cx,cy,rx,ry,0,0,Math.PI*2);x.fill();};oval(320,480,170,150,'#88927c');oval(320,230,110,150,'#1a231b');oval(320,250,83,113,'#cbd1ab');oval(320,150,94,55,'#263326');oval(288,238,10,7,'#263326');oval(352,238,10,7,'#263326');oval(322,275,10,18,'#8b9876');x.strokeStyle='#58674d';x.lineWidth=5;x.beginPath();x.arc(320,292,28,0.2,Math.PI-0.2);x.stroke();result(c,true);}
$('switch').onclick=()=>{if(state==='preview'&&switchAvailable)start(selectedFacing==='user'?'environment':'user',true);else if(state==='preview')$('status').textContent='Only one camera detected; switching is unavailable.';else unavailable();};$('capture').onclick=capture;
$('density').oninput=()=>{syncDial();if(['preview','result'].includes(state))render(state==='result'?image:$('video'));else $('status').textContent='Density set. Camera power is unchanged.';};
$('copy').onclick=async()=>{if(!['preview','result'].includes(state)){unavailable();return;}const text=$('ascii').textContent,token=epoch;try{if(!window.isSecureContext||!navigator.clipboard?.writeText)throw new Error();await navigator.clipboard.writeText(text);if(token===epoch)$('status').textContent='ASCII text copied (frame at click).';}catch{if(token===epoch){$('status').textContent='Copy unavailable or denied. Select the ASCII text and copy it manually.';const range=document.createRange();range.selectNodeContents($('ascii'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);}}};
$('power').onclick=()=>{if(sessionPower)reset();else start();};
$('save').onclick=()=>{if(state!=='result'){unavailable();return;}const lines=$('ascii').textContent.split('\n'),c=document.createElement('canvas');c.width=Math.ceil(geometry.width)+64;c.height=Math.ceil(geometry.height)+112;const x=c.getContext('2d');x.fillStyle='#08160f';x.fillRect(0,0,c.width,c.height);x.fillStyle='#b4f5b0';x.save();x.translate(32,32);x.drawImage(flat,0,0,Math.ceil(geometry.width),Math.ceil(geometry.height));x.restore();const footer=demo?'ASCamera - FATQ / DEMO':'ASCamera - FATQ';x.font='12px monospace';const footerSize=Math.min(12,12*(c.width-64)/x.measureText(footer).width);x.font=`${footerSize}px monospace`;x.fillText(footer,32,c.height-45);c.toBlob(blob=>{if(!blob)return;const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;const now=new Date();const stamp=`${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}-${String(now.getHours()).padStart(2,'0')}${String(now.getMinutes()).padStart(2,'0')}${String(now.getSeconds()).padStart(2,'0')}-${String(now.getMilliseconds()).padStart(3,'0')}`;a.download=`ascamera-${demo?'demo':'portrait'}-${stamp}.png`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);},'image/png');};
$('video').addEventListener('resize',fit);window.addEventListener('resize',fit);window.addEventListener('pagehide',()=>reset());document.addEventListener('visibilitychange',()=>{if(document.hidden&&sessionPower)reset('Camera session closed because this tab was hidden.');});show('idle','Ready when you are. Camera access is optional.');

// Align the four planar faces to the actual responsive glass bounds, not guessed percentages.
function alignRecess(){const b=document.querySelector('.bezel').getBoundingClientRect(),s=document.querySelector('.screen').getBoundingClientRect();const l=(s.left-b.left)/b.width*100,r=(s.right-b.left)/b.width*100,t=(s.top-b.top)/b.height*100,d=(s.bottom-b.top)/b.height*100,w=r-l,h=d-t;
// One normalized aperture: alternating bowed sides and explicit quadratic corners.
const start=[.06,.025], segments=[[[.5,.005],[.94,.025]],[[.975,.027],[.978,.065]],[[.995,.5],[.978,.935]],[[.975,.973],[.94,.975]],[[.5,.995],[.06,.975]],[[.025,.973],[.022,.935]],[[.005,.5],[.022,.065]],[[.025,.027],start]];
const point=p=>`${l+w*p[0]} ${t+h*p[1]}`,q=(c,e)=>` Q ${point(c)} ${point(e)}`;
document.querySelector('#smooth-aperture path').setAttribute('d','M '+start.join(' ')+segments.map(([c,e])=>' Q '+c.join(' ')+' '+e.join(' ')).join('')+' Z');
const corners=[1,3,5,7].map(i=>{const a=segments[i-1][1],c=segments[i][0],e=segments[i][1];return {mid:a.map((v,j)=>(v+2*c[j]+e[j])/4),first:a.map((v,j)=>(v+c[j])/2),last:c.map((v,j)=>(v+e[j])/2)};});
const [tr,br,bl,tl]=corners;
const inner=[`M ${point(tl.mid)}`+q(tl.last,start)+q(...segments[0])+q(tr.first,tr.mid),`M ${point(tr.mid)}`+q(tr.last,segments[1][1])+q(...segments[2])+q(br.first,br.mid),`M ${point(br.mid)}`+q(br.last,segments[3][1])+q(...segments[4])+q(bl.first,bl.mid),`M ${point(bl.mid)}`+q(bl.last,segments[5][1])+q(...segments[6])+q(tl.first,tl.mid)];
// Trace inner boundary clockwise, then close through the corresponding outer corners.
const outer=[' L 100 0 L 0 0 Z',' L 100 100 L 100 0 Z',' L 0 100 L 100 100 Z',' L 0 0 L 0 100 Z'];
document.querySelectorAll('.facet').forEach((p,i)=>p.setAttribute('d',inner[i]+outer[i]));
const endpoints=[tl,tr,br,bl].map(c=>point(c.mid));document.querySelectorAll('.crease-lines path').forEach((p,i)=>p.setAttribute('d',`M ${['0 0','100 0','100 100','0 100'][i]} L ${endpoints[i]}`));
document.querySelector('.bezel-faces').dataset.cornerPoints=JSON.stringify(endpoints.map(p=>p.split(' ').map(Number)));
}

new ResizeObserver(alignRecess).observe(document.querySelector('.bezel'));alignRecess();

const ARC_START=-135, ARC_SWEEP=270;
function syncDial(){const v=Number($('density').value);$('boot-density').textContent=String(v).padStart(3,'0');$('density-value').textContent=`DENSITY ${String(v).padStart(3,'0')}`;$('density-box').style.setProperty('--knob-angle',`${ARC_START+(v-40)/120*ARC_SWEEP}deg`);$('density').setAttribute('aria-valuetext',`${v} columns`);}
let knobDrag=null;
$('density').addEventListener('pointerdown',e=>{if($('density').disabled)return;e.preventDefault();$('density').focus();$('density').setPointerCapture(e.pointerId);knobDrag={x:e.clientX,y:e.clientY,value:Number($('density').value)};});
$('density').addEventListener('pointermove',e=>{if(!knobDrag)return;e.preventDefault();const v=Math.max(40,Math.min(160,Math.round((knobDrag.value+(e.clientX-knobDrag.x)-(e.clientY-knobDrag.y))/8)*8));$('density').value=v;syncDial();$('density').dispatchEvent(new Event('input'));});
for(const name of ['pointerup','pointercancel','lostpointercapture'])$('density').addEventListener(name,()=>knobDrag=null);
$('density').addEventListener('input',syncDial);syncDial();

const scaleTrack=document.querySelector('.density-track');for(let i=0;i<=10;i++){const tick=document.createElement('span');tick.className='scale-mark';tick.setAttribute('aria-hidden','true');tick.style.transform=`rotate(${ARC_START+i*ARC_SWEEP/10}deg) translateY(-39px)`;scaleTrack.append(tick);}for(const [name,text] of [['min','40'],['max','160']]){const n=document.createElement('span');n.className=`scale-number ${name}`;n.textContent=text;n.setAttribute('aria-hidden','true');scaleTrack.append(n);}

const dotArm=document.createElement('span');dotArm.className='knob-dot-arm';dotArm.setAttribute('aria-hidden','true');dotArm.innerHTML='<span class="knob-dot"></span>';document.querySelector('.density-control').append(dotArm);

// Scale the complete desktop console (screen + controls) to the real viewport height.
function fitMachine(){
  const machine=document.querySelector('.machine');
  if(!machine)return;
  if(window.innerWidth<=600){document.documentElement.style.removeProperty('--fit-scale');return;}
  const zoom=parseFloat(getComputedStyle(machine).zoom)||1;
  const rect=machine.getBoundingClientRect();
  const naturalW=rect.width/zoom,naturalH=rect.height/zoom;
  const scale=Math.min(1,(window.innerHeight-96)/naturalH,(window.innerWidth-112)/naturalW);
  document.documentElement.style.setProperty('--fit-scale',String(Math.max(.5,scale)));
}
requestAnimationFrame(fitMachine);
window.addEventListener('load',fitMachine,{once:true});
window.addEventListener('resize',fitMachine);
