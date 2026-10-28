# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Local-only tests. Camera replaced by canvas stream; never real hardware."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import urllib.request
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
MOCK = """window.calls=0;window.streams=[];window.mode='ok';
Object.defineProperty(navigator.mediaDevices,'enumerateDevices',{value:async()=>window.reportFacing==='single'?[{kind:'videoinput',deviceId:'front'}]:window.reportFacing==='dual'?[{kind:'videoinput',deviceId:'front'},{kind:'videoinput',deviceId:'rear'}]:[]});
Object.defineProperty(navigator.mediaDevices,'getUserMedia',{value: async options=>{
 window.calls++;window.options=options;
 if(window.mode==='denied')throw new DOMException('Denied','NotAllowedError');
 if(window.mode==='missing'||(window.mode==='rear-fails'&&(options.video.deviceId?.exact==='rear'||options.video.facingMode?.ideal==='environment')))throw new DOMException('Missing','NotFoundError');
 const c=document.createElement('canvas');c.width=window.fixtureWidth||640;c.height=window.fixtureHeight||480;const x=c.getContext('2d');x.fillStyle='white';x.fillRect(0,0,320,480);x.fillStyle='black';x.fillRect(320,0,320,480);
 if(window.fixtureWidth){
 x.fillStyle='#777';x.fillRect(0,0,c.width,c.height);
 const b=Math.ceil(Math.min(c.width,c.height)*.12);
 x.fillStyle='red';x.fillRect(0,0,c.width,b);x.fillStyle='lime';x.fillRect(0,c.height-b,c.width,b);
 x.fillStyle='blue';x.fillRect(0,0,b,c.height);x.fillStyle='white';x.fillRect(c.width-b,0,b,c.height);
 x.fillStyle='black';x.fillRect(c.width*.3,c.height*.3,b,b);
 }window.fixture=c;
 const stream=c.captureStream(10);if(window.reportFacing){const t=stream.getVideoTracks()[0];const get=t.getSettings.bind(t);t.getSettings=()=>({...get(),deviceId:(window.reportFacing==='single'||window.sameDevice)?'front':options.video.deviceId?.exact||(options.video.facingMode?.ideal==='environment'?'rear':'front'),facingMode:window.reportFacing==='single'?'user':(options.video.deviceId?.exact==='rear'||options.video.facingMode?.ideal==='environment'?'environment':'user')});}else{stream.getVideoTracks()[0].getSettings=()=>({});}window.streams.push(stream);
 if(window.mode==='pending')await new Promise(resolve=>window.release=resolve);
 return stream;
}});"""


def main():
    checks = []
    server = subprocess.Popen([sys.executable, str(HERE/'start.py'), '--no-browser', '--port', '18765'], cwd=tempfile.gettempdir(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen('http://127.0.0.1:18765/', timeout=1).close()
                break
            except OSError:
                time.sleep(.05)
        conflict = subprocess.run([sys.executable, str(HERE/'start.py'), '--no-browser', '--port', '18765'], capture_output=True, text=True)
        assert conflict.returncode == 1 and 'use --port 8766' in conflict.stderr
        checks.append('launcher: other cwd and occupied port')
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
            page = browser.new_page(accept_downloads=True)
            page.add_init_script(MOCK)
            errors, external = [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('request', lambda req: external.append(req.url) if not req.url.startswith(('http://127.0.0.1:', 'blob:', 'data:')) else None)
            def fresh(mode='ok'):
                page.goto('http://127.0.0.1:18765/')
                page.evaluate('(mode)=>window.mode=mode', mode)
            def fixture():
                page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.click('#capture')
            def stopped():
                return page.evaluate('streams.every(s=>s.getTracks().every(t=>t.readyState==="ended"))')
            fresh()
            assert page.evaluate('calls') == 0
            checks.append('no automatic permission request')
            fixture()
            assert 'SNAPSHOT' in page.inner_text('#source')
            assert 30 <= len(page.locator('#ascii').text_content().splitlines()) <= 40
            page.locator('#density').evaluate("el=>{el.value=160;el.dispatchEvent(new Event('input'));}")
            assert len(page.inner_text('#ascii').splitlines()[0]) == 160
            assert page.evaluate('calls') == 1
            checks.append('synthetic camera fixture and frozen density')
            with page.expect_download() as info:
                page.click('#save')
            download = info.value
            assert download.suggested_filename.startswith('ascamera-portrait-') and download.suggested_filename.endswith('.png')
            assert Path(download.path()).read_bytes()[:8] == b'\x89PNG\r\n\x1a\n'
            checks.append('synthetic frozen PNG download')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900})
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                page.screenshot(path=str(Path(tempfile.gettempdir())/f'phosphor-demo-{width}.png'), full_page=True)
            checks.append('synthetic desktop/mobile no overflow and screenshots')
            page.click('#power')
            assert page.inner_text('#ascii') == ''
            checks.append('close clears image')
            for mode, text in [('denied','permission denied'),('missing','No camera found')]:
                fresh(mode);page.click('#power');page.wait_for_function('(text)=>document.querySelector("#status").textContent.includes(text)', arg=text)
                assert stopped()
                checks.append(f'{mode} recovery message')
            fresh('pending');page.click('#power');page.wait_for_function('window.release!==undefined');page.click('#power');page.evaluate('release()');page.wait_for_function('streams[0].getTracks()[0].readyState==="ended"')
            assert page.locator('#power').is_visible()
            checks.append('late permission after close stops stream')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert page.evaluate('options.audio') is False
            page.click('#capture');page.wait_for_function('document.querySelector("#physical-led").dataset.state==="captured"');assert not stopped()
            lines=page.inner_text('#ascii').splitlines();assert lines[0][0]==' ' and lines[0][-1]=='@'
            assert 'CAMERA ACTIVE' in page.inner_text('#lamp')
            checks.append('immediate single mirrored snapshot and track cleanup')
            page.click('#capture');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert page.evaluate('calls') == 1
            page.evaluate('streams[0].getVideoTracks()[0].dispatchEvent(new Event("ended"))')
            page.wait_for_function('document.querySelector("#status").textContent.includes("interrupted")');assert stopped()
            checks.append('retake explicit restart and interruption cleanup')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.click('#capture');page.click('#power');page.wait_for_timeout(300);assert stopped() and page.locator('#power').is_visible()
            checks.append('close cancels scheduled snapshot')
            fresh('pending');page.click('#power');page.wait_for_function('window.release!==undefined');page.evaluate('window.dispatchEvent(new Event("pagehide"));release()');page.wait_for_function('streams[0].getTracks()[0].readyState==="ended"')
            checks.append('pagehide invalidates pending permission')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.evaluate('Object.defineProperty(document,"hidden",{value:true,configurable:true});document.dispatchEvent(new Event("visibilitychange"))');assert stopped()
            checks.append('hidden tab releases camera')
            fresh('pending');page.click('#power');page.wait_for_function('window.release!==undefined');page.click('#power');page.evaluate('window.mode="ok"');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.evaluate('release()');page.wait_for_function('streams[0].getTracks()[0].readyState==="ended"');assert page.evaluate('streams[1].getTracks()[0].readyState') == 'live';page.click('#power');assert stopped()
            checks.append('old permission cannot replace new camera session')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.evaluate('window.dispatchEvent(new Event("pagehide"))');assert stopped()
            checks.append('pagehide stops active stream')
            fresh();page.evaluate('Object.defineProperty(navigator,"mediaDevices",{value:undefined})');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("API unavailable")')
            checks.append('unavailable API recovery')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.evaluate('Object.defineProperty(document.querySelector("#video"),"readyState",{value:0})');page.click('#capture');assert 'warming up' in page.inner_text('#status');assert page.locator('#count').count()==0;page.click('#power');assert stopped()
            checks.append('unready frame does not start capture')
            for viewport in [1200,400]:
                page.set_viewport_size({'width':viewport,'height':900})
                for w,h in [(640,480),(960,540),(480,640),(540,960)]:
                    fresh();page.evaluate('([w,h])=>{window.fixtureWidth=w;window.fixtureHeight=h}',[w,h])
                    page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
                    def bounds():
                        return page.evaluate("""()=>{const r=document.querySelector('#viewfinder').getBoundingClientRect(),s=document.querySelector('#stage').getBoundingClientRect();return {w:r.width,h:r.height,inside:r.left>=s.left-1&&r.right<=s.right+1&&r.top>=s.top-1&&r.bottom<=s.bottom+1}}""")
                    preview=bounds();assert preview['inside'] and abs(preview['w']/preview['h']-w/h)<.01
                    page.click('#capture');page.wait_for_function('document.querySelector("#physical-led").dataset.state==="captured"')
                    for density in [40,96,160]:
                        page.locator('#density').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input"))}',density)
                        result=bounds();assert abs(result['w']-preview['w'])<1 and abs(result['h']-preview['h'])<1
                        grid=page.locator('#ascii').text_content().split('\n')
                        assert all(row[0]=='@' and row[-1]=='.' for row in grid), 'mirrored side edges lost'
                        assert grid[0][len(grid[0])//2]==':' and grid[-1][len(grid[-1])//2]=='*', 'top/bottom lost'
                        assert ' ' in grid[len(grid)//3], 'interior fiducial lost'
                        with page.expect_download() as info:page.click('#save')
                        import base64
                        encoded=base64.b64encode(Path(info.value.path()).read_bytes()).decode('ascii')
                        png=page.evaluate("""async data=>{const i=new Image();i.src='data:image/png;base64,'+data;await i.decode();const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);const p=x.getImageData(0,0,c.width,c.height).data;let outside=0,photo=0,footer=0;const end=c.height-80;for(let y=0;y<c.height;y++)for(let xx=0;xx<c.width;xx++){const k=(y*c.width+xx)*4;if(p[k]===180&&p[k+1]===245){if(y>=32&&y<end&&xx>=32&&xx<c.width-32)photo++;else if(y>=end)footer++;else outside++;}}return {w:c.width-64,h:c.height-112,outside,photo,footer}}""",encoded)
                        assert abs(png['w']/png['h']-w/h)<.02 and png['outside']==0 and png['photo']>0 and png['footer']>0,png
                    checks.append(f'full frame edges/fiducial, PNG bounds and 3 densities: {w}x{h} at {viewport}px')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            assert page.locator('#ascii').is_visible() and page.locator('#video').is_hidden()
            assert len(page.locator('#ascii').text_content().split('\n')[0])==96
            page.evaluate("""()=>{window.liveTimes=[];window.liveObserver=new MutationObserver(()=>liveTimes.push(performance.now()));liveObserver.observe(document.querySelector('#ascii'),{childList:true});window.frameTimer=setInterval(()=>{const x=fixture.getContext('2d');x.fillStyle=(window.phase=!window.phase)?'white':'black';x.fillRect(0,0,fixture.width,fixture.height)},100)}""")
            before=page.locator('#ascii').text_content()
            page.wait_for_function('(before)=>document.querySelector("#ascii").textContent!==before',arg=before)
            page.wait_for_timeout(1400)
            metrics=page.evaluate("""()=>{const t=liveTimes;return {updates:t.length,elapsedMs:t.at(-1)-t[0],fps:(t.length-1)*1000/(t.at(-1)-t[0]),minimumIntervalMs:Math.min(...t.slice(1).map((v,i)=>v-t[i]))}}""")
            assert 8<metrics['fps']<=21 and metrics['minimumIntervalMs']>35,metrics
            checks.append('synthetic video progresses in live ASCII with measured throttled updates')
            for density in [40,160,96]:
                page.locator('#density').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input"))}',density)
                assert len(page.locator('#ascii').text_content().split('\n')[0])==density
            checks.append('live density updates without requesting another stream')
            page.click('#capture');page.wait_for_function('document.querySelector("#physical-led").dataset.state==="captured"')
            frozen=page.locator('#ascii').text_content();count=page.evaluate('liveTimes.length');page.wait_for_timeout(300)
            assert page.locator('#ascii').text_content()==frozen and page.evaluate('liveTimes.length')==count and not stopped()
            with page.expect_download() as info:page.click('#save')
            assert Path(info.value.path()).read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
            checks.append('capture freezes ASCII and scheduling, retains camera and saves PNG')
            page.click('#capture');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');count=page.evaluate('liveTimes.length');page.wait_for_timeout(250)
            assert page.evaluate('liveTimes.length')>count and page.evaluate('calls')==1
            page.click('#power');count=page.evaluate('liveTimes.length');page.wait_for_timeout(250)
            assert page.evaluate('liveTimes.length')==count and stopped() and page.locator('#ascii').text_content()==''
            page.evaluate('clearInterval(frameTimer)')
            checks.append('capture resumes existing stream; power off cancels all live updates')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            page.evaluate("Object.defineProperty(document,'hidden',{value:true,configurable:true});document.dispatchEvent(new Event('visibilitychange'))")
            page.wait_for_timeout(250)
            assert stopped() and page.locator('#ascii').text_content()=='' and page.locator('#power').is_visible()
            checks.append('hidden tab stops live preview and clears ASCII')
            fresh();page.evaluate('window.reportFacing="dual"');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            assert page.locator('#ascii').text_content()[0]==' ' and 'FRONT' in page.inner_text('#source')
            page.locator('#density').evaluate('el=>{el.value=80;el.dispatchEvent(new Event("input"))}')
            page.click('#switch');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.wait_for_function('document.querySelector("#ascii").textContent.length>0')
            assert page.evaluate('streams[0].getTracks()[0].readyState')=='ended'
            assert page.locator('#ascii').text_content()[0]=='@' and 'UNMIRRORED' in page.inner_text('#source')
            assert len(page.locator('#ascii').text_content().split('\n')[0])==80
            assert page.evaluate('options.audio') is False and page.evaluate('options.video.deviceId.exact')=='rear'
            checks.append('front/rear switch stops old tracks, preserves density and uses actual facing')
            page.click('#capture');page.wait_for_function('document.querySelector("#physical-led").dataset.state==="captured"')
            assert page.locator('#ascii').text_content()[0]=='@' and page.locator('#switch').is_enabled() and not stopped()
            with page.expect_download() as info:page.click('#save')
            assert Path(info.value.path()).read_bytes()[:8]==b'\x89PNG\r\n\x1a\n'
            checks.append('rear capture/frozen/export remains unmirrored; switching unavailable during capture')
            for facing,mode,text in [('dual','rear-fails','restored'),(None,'ok','cannot be verified')]:
                fresh();page.evaluate('([f,m])=>{window.reportFacing=f;window.mode=m}',[facing,mode]);page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
                page.click('#switch');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert text in page.inner_text('#status'), (facing,mode,page.inner_text('#status'))
                assert page.evaluate('streams.filter(s=>s.getTracks()[0].readyState==="live").length')==1
                page.click('#power');assert stopped()
                checks.append(f'switch fallback reports actual availability: {facing}/{mode}')
            fresh();page.evaluate('window.reportFacing="dual"');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            page.evaluate('window.mode="pending"');page.click('#switch');page.wait_for_function('window.release!==undefined');assert page.locator('#switch').is_enabled()
            assert page.evaluate('streams[0].getTracks()[0].readyState')=='ended'
            page.click('#power');page.evaluate('release()');page.wait_for_function('streams.every(s=>s.getTracks()[0].readyState==="ended")')
            assert page.locator('#power').is_visible() and page.locator('#ascii').text_content()==''
            checks.append('close during pending switch invalidates and stops late stream')
            fresh();page.evaluate('window.reportFacing="dual";window.sameDevice=true');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            before=page.locator('#ascii').text_content();page.click('#switch');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            assert page.locator('#ascii').text_content()==before and 'orientation unchanged' in page.inner_text('#status')
            page.click('#power');assert stopped()
            checks.append('same-device return cannot flip orientation even with contradictory facing report')
            fresh();page.evaluate('window.reportFacing="single"');page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            before=page.locator('#ascii').text_content();assert page.locator('#switch').is_enabled() and 'Only one camera' in page.inner_text('#status')
            page.evaluate('document.querySelector("#switch").click()');page.wait_for_timeout(200)
            assert page.evaluate('calls')==1 and page.locator('#ascii').text_content()==before
            checks.append('single physical camera switch explains unavailability without flip or new request')
            fresh();page.evaluate("""()=>{window.writes=[];Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>writes.push(text)}})}""")
            fixture();assert page.evaluate('writes.length')==0
            expected=page.locator('#ascii').text_content();page.click('#copy');page.wait_for_function('document.querySelector("#status").textContent.includes("copied")')
            assert page.evaluate('writes')==[expected]
            checks.append('explicit frozen ASCII copy writes exact whitespace and no automatic clipboard writes')
            page.click('#capture');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');expected=page.locator('#ascii').text_content();page.click('#copy');page.wait_for_function('writes.length===2');assert page.evaluate('writes[1]')==expected
            checks.append('live ASCII copy uses displayed frame at click')
            for mode in ['denied','unsupported']:
                page.evaluate("""mode=>{Object.defineProperty(navigator,'clipboard',{configurable:true,value:mode==='unsupported'?undefined:{writeText:async()=>{throw new DOMException('Denied','NotAllowedError')}}})}""",mode)
                page.click('#copy');page.wait_for_function('document.querySelector("#status").textContent.includes("Copy unavailable")')
                assert page.evaluate('getSelection().toString()')==page.locator('#ascii').text_content()
                checks.append(f'clipboard {mode} reports failure and selects text without fake success')
            page.click('#power');assert stopped()
            fresh();page.focus('#power');page.keyboard.press('Space');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            assert page.locator('#power').get_attribute('aria-checked')=='true' and page.evaluate('calls')==1
            page.focus('#density');page.keyboard.press('ArrowRight');assert page.locator('#density').input_value()=='104'
            assert len(page.locator('#ascii').text_content().split('\n')[0])==104
            assert page.locator('.dial').count()==0
            checks.append('native density keyboard adjustment updates grid through accessible linear fader')
            page.focus('#power');page.keyboard.press('Space');assert stopped() and page.locator('#power').get_attribute('aria-checked')=='false'
            checks.append('keyboard power toggle explicitly requests and releases video')
            fixture()
            lever=page.locator('#density');lever.scroll_into_view_if_needed();rect=lever.bounding_box();page.mouse.move(rect['x']+rect['width']*.53,rect['y']+rect['height']/2);page.mouse.down();page.mouse.move(rect['x']+rect['width']*.95,rect['y']+rect['height']/2-40,steps=8);page.mouse.up()
            assert int(lever.input_value())>104 and len(page.locator('#ascii').text_content().split('\n')[0])==int(lever.input_value())
            checks.append('native fader pointer drag updates actual density')
            warp=page.evaluate("""async()=>{const {paintCRT,crtPoint}=await import('./crt.js');const s=document.createElement('canvas');s.width=400;s.height=300;const x=s.getContext('2d');x.fillStyle='white';x.fillRect(0,0,400,300);x.fillStyle='red';x.fillRect(0,0,400,4);x.fillStyle='lime';x.fillRect(0,296,400,4);const c=document.createElement('canvas');c.width=400;c.height=300;const y=c.getContext('2d');paintCRT(y,s,400,300);const a=crtPoint(0,0),b=crtPoint(.5,0);const d=y.getImageData(0,0,400,300).data;const greenAt=(u,v)=>d[(Math.round(v)*400+Math.round(u))*4+1];return {corner:a,mid:b,center:greenAt(200,150),topCenter:greenAt(200,3),topCorner:greenAt(25,19)}}""")
            assert warp['corner']['y']-warp['mid']['y']>.05 and warp['center']>200 and warp['topCenter']<100
            checks.append('synthetic colored edges show measurable barrel curvature and padded full-frame mapping')
            fresh()
            common=page.evaluate("""()=>{const c=document.querySelector('.screen-content');return {filter:getComputedStyle(c).filter,welcome:c.contains(document.querySelector('#welcome')),header:c.contains(document.querySelector('.screen-top')),footer:c.contains(document.querySelector('.screen-bottom')),picture:c.contains(document.querySelector('#crt')),console:c.contains(document.querySelector('.console')),map:document.querySelector('#curve-map').getAttribute('href'),scale:document.querySelector('feDisplacementMap').getAttribute('scale')}}""")
            assert 'screen-curve' in common['filter'] and all(common[k] for k in ['welcome','header','footer','picture']) and not common['console']
            assert common['map'].startswith('data:image/png') and common['scale']=='12'
            fixture();assert page.locator('.screen-content #crt').is_visible()
            assert page.evaluate('getComputedStyle(document.querySelector("#crt")).filter')=='none'
            checks.append('one subtle common screen displacement includes welcome/status/photo and excludes physical controls')
            fresh();assert page.locator('header,.machine-top,#start,#cancel,#count').count()==0
            assert page.evaluate('document.querySelector(".power-bank").contains(document.querySelector("#power"))')
            assert page.locator('#physical-led').get_attribute('data-state')=='off'
            page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert page.locator('#physical-led').get_attribute('data-state')=='live'
            page.click('#capture');assert page.locator('#save').is_visible() and not stopped() and page.locator('#physical-led').get_attribute('data-state')=='captured'
            assert page.evaluate('!document.querySelector(".screen").contains(document.querySelector("#physical-led"))')
            checks.append('unbranded case, bottom-left sole power entry, immediate freeze and external LED states')
            direction=page.evaluate("""async()=>{const i=new Image();i.src=document.querySelector('#curve-map').getAttribute('href');await i.decode();const c=document.createElement('canvas');c.width=128;c.height=128;const x=c.getContext('2d');x.drawImage(i,0,0);const d=x.getImageData(0,0,128,128).data;return {right:d[(64*128+127)*4],left:d[(64*128)*4],top:d[64*4+1],bottom:d[(127*128+64)*4+1]}}""")
            assert direction['right']<128 and direction['left']>128 and direction['top']>128 and direction['bottom']<128
            checks.append('calibrated displacement samples pull source inward so visible grid moves outward convex')
            housing=page.evaluate("""()=>{const s=document.querySelector('.screen'),b=document.querySelector('.bezel'),c=document.querySelector('.screen-content');return {aperture:getComputedStyle(s).clipPath,funnel:getComputedStyle(b).backgroundImage,gasket:getComputedStyle(b,'::after').backgroundColor,inside:c.getBoundingClientRect().left>s.getBoundingClientRect().left}}""")
            assert 'smooth-aperture' in housing['aperture']  and housing['inside']
            checks.append('sculpted funnel and separate gasket surround bowed aperture with content inset')
            smooth=page.evaluate("""()=>({units:document.querySelector('#smooth-aperture').getAttribute('clipPathUnits'),path:document.querySelector('#smooth-aperture path').getAttribute('d'),faces:document.querySelectorAll('.bezel-faces .facet').length,seams:document.querySelectorAll('.crease-lines path').length,events:getComputedStyle(document.querySelector('.bezel-faces')).pointerEvents})""")
            assert smooth['units']=='objectBoundingBox' and smooth['path'].count('Q')==8 and 'L' not in smooth['path'] and smooth['faces']==4 and smooth['seams']==4 and smooth['events']=='none'
            checks.append('continuous near-rectangular aperture with four planar faces and four inward miter seams')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh();fixture()
                page.evaluate("""()=>{const c=document.querySelector('.screen-content');for(const side of ['top','bottom'])for(const edge of ['left','right']){const m=document.createElement('span');m.className='pixel-landmark';Object.assign(m.style,{position:'absolute',width:'8px',height:'8px',background:'#ff00ff',zIndex:10,[side]:'0px',[edge]:'0px'});c.append(m)}}""")
                import base64
                shot=page.locator('.screen').screenshot()
                pixels=page.evaluate("""async b=>{const i=new Image();i.src='data:image/png;base64,'+b;await i.decode();const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);const d=x.getImageData(0,0,c.width,c.height).data,q=[0,0,0,0];for(let y=0;y<c.height;y++)for(let xx=0;xx<c.width;xx++){const k=(y*c.width+xx)*4;if(d[k]>180&&d[k+1]<60&&d[k+2]>180)q[(y>c.height/2?2:0)+(xx>c.width/2?1:0)]++;}return q}""",base64.b64encode(shot).decode('ascii'))
                assert all(n>=30 for n in pixels), (width,pixels)
                page.evaluate('document.querySelectorAll(".pixel-landmark").forEach(e=>e.remove())')
                page.screenshot(path=str(Path(tempfile.gettempdir())/f'phosphor-repaired-{width}.png'),full_page=True)
                checks.append(f'rendered screenshot preserves four status-region corner landmarks at {width}px')
            for width in [1200,400,1200]:
                page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(100)
                matches=page.evaluate("""()=>{const b=document.querySelector('.bezel').getBoundingClientRect(),s=document.querySelector('.screen').getBoundingClientRect();const norm=[[.033,.036],[.967,.036],[.967,.964],[.033,.964]];return [...document.querySelectorAll('.crease-lines path')].every((p,i)=>{const n=p.getAttribute('d').match(/L (.*)/)[1].split(' ').map(Number),e=[((s.left-b.left)+s.width*norm[i][0])/b.width*100,((s.top-b.top)+s.height*norm[i][1])/b.height*100];return Math.abs(n[0]-e[0])<1e-8&&Math.abs(n[1]-e[1])<1e-8&&[...document.querySelectorAll('.facet')].filter(f=>f.getAttribute('d').includes(n.join(' '))).length===2;})}""")
                assert matches,width
            checks.append('all seam endpoints equal exact quadratic corner midpoints and two face endpoints through desktop/mobile resize')
            fresh()
            def panel():
                return page.evaluate("""()=>[...document.querySelectorAll('button')].map(b=>{const r=b.getBoundingClientRect();return {id:b.id,x:r.x+scrollX,y:r.y+scrollY,w:r.width,h:r.height}})""")
            base=panel();assert page.locator('#density').is_visible() and page.locator('#density').is_enabled()
            page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert panel()==base
            page.click('#capture');assert panel()==base and page.locator('#density').is_enabled()
            page.focus('#density');page.keyboard.press('Home');assert page.locator('#density').input_value()=='40';page.keyboard.press('End');assert page.locator('#density').input_value()=='160'
            assert len(page.locator('#ascii').text_content().split('\n')[0])==160
            checks.append('all buttons retain identical slots through idle/live/frozen; rotary Home/End changes actual grid')
            for width in [1200,400,1200]:
                page.set_viewport_size({'width':width,'height':900});page.wait_for_timeout(100)
                physical=page.evaluate("""()=>{const b=document.querySelector('.bezel').getBoundingClientRect(),k=document.querySelector('.control-panel').getBoundingClientRect(),m=document.querySelector('.machine'),input=document.querySelector('#density').getBoundingClientRect(),track=document.querySelector('.density-track'),panel=document.querySelector('.density-control').getBoundingClientRect();const a=getComputedStyle(track,'::before'),c=getComputedStyle(track,'::after');return {left:Math.abs(b.left-k.left),right:Math.abs(b.right-k.right),gutter:parseFloat(getComputedStyle(m).paddingLeft),top:parseFloat(getComputedStyle(m).paddingTop),ring:[parseFloat(a.left),parseFloat(a.top)],cap:[parseFloat(c.left),parseFloat(c.top)],input:[(input.x+input.width/2-panel.x)/(panel.width/document.querySelector('.density-control').offsetWidth),(input.y+input.height/2-panel.y)/(panel.width/document.querySelector('.density-control').offsetWidth)]}}""")
                assert physical['gutter']>=12 and physical['top']==physical['gutter']
                assert physical['ring']==physical['cap'] and all(abs(a-b)<2 for a,b in zip(physical['ring'],physical['input'])),physical
            checks.append('shared thick housing gutters and concentric ring/cap/input centers across desktop/mobile resize')
            fresh()
            def material():
                return page.locator('#capture').evaluate("el=>{const s=getComputedStyle(el);return [s.opacity,s.color,s.backgroundImage,s.boxShadow,s.filter,s.borderColor,s.borderRadius]}")
            disabled=material();assert page.locator('#capture').is_enabled()
            assert page.evaluate('document.querySelector(".screen-content").contains(document.querySelector("#density-value"))')
            label=page.locator('label[for=density]').text_content()
            page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert material()==disabled
            page.locator('#density').evaluate('el=>{el.value=160;el.dispatchEvent(new Event("input"))}')
            assert page.locator('label[for=density]').text_content()==label and page.locator('#density-value').text_content()=='DENSITY 160'
            checks.append('density counter is CRT-only; off and live keycap materials remain identical')
            fresh();assert page.locator('#demo').count()==0
            actions=['switch','copy','save']
            for action in actions:
                assert page.locator('#'+action).is_enabled() and page.locator('#'+action).is_visible()
                page.click('#'+action);assert page.inner_text('#status')=='Turn on camera power first.' and page.evaluate('calls')==0
            page.focus('#density');page.keyboard.press('End');assert page.locator('#density').input_value()=='160' and page.locator('#density-value').text_content()=='DENSITY 160' and page.evaluate('calls')==0
            assert page.evaluate('document.querySelector(".screen-content").contains(document.querySelector("#status"))')
            checks.append('every off-state action gives power-first hint without permission; knob changes stored density')
            fresh('pending');page.click('#power');page.wait_for_function('window.release!==undefined')
            for action in ['capture','switch','copy','save']:
                page.click('#'+action);assert 'Waiting for camera permission' in page.inner_text('#status') and page.evaluate('calls')==1
            page.click('#power');page.evaluate('release()');page.wait_for_function('streams.every(s=>s.getTracks()[0].readyState==="ended")')
            checks.append('requesting actions remain enabled without duplicate requests; power cancels late stream')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                layout=page.evaluate("""()=>{const rect=s=>document.querySelector(s).getBoundingClientRect(),p=rect('#power'),d=rect('#density'),c=rect('.control-column'),k=rect('.buttons');const keys=[...document.querySelectorAll('.buttons button')].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}});return {stack:Math.abs((p.top+p.bottom-d.top-d.bottom)/2)<15,side:c.right<=k.left||innerWidth<=600,aligned:Math.abs(c.bottom-k.bottom)<1,keys}}""")
                keys=layout['keys'];assert layout['stack'] and layout['side'] and (layout['aligned'] or width<=600) and len(keys)==4
                assert len(set(round(k['x']) for k in keys))==4 and len(set(round(k['y']) for k in keys))==1 and all(k['w']>=44 and k['h']>=44 for k in keys)
            checks.append('side-by-side power and knob bank beside single-row four-key keyboard at desktop/mobile touch sizes')
            fresh();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")')
            for _ in range(3):
                page.click('#capture');assert page.locator('#power').get_attribute('aria-checked')=='true' and not stopped() and 'CAMERA ACTIVE' in page.inner_text('#lamp')
                page.click('#capture');assert page.locator('#power').get_attribute('aria-checked')=='true' and page.evaluate('calls')==1
            page.click('#capture');page.evaluate('Object.defineProperty(document,"hidden",{value:true,configurable:true});document.dispatchEvent(new Event("visibilitychange"))')
            assert stopped() and page.locator('#power').get_attribute('aria-checked')=='false' and page.locator('#ascii').text_content()==''
            checks.append('capture repeatedly freezes/resumes one powered camera stream; hidden frozen session fully powers off')
            fresh();page.locator('#power').scroll_into_view_if_needed()
            def switch_shape():
                return page.locator('#power').evaluate("""el=>{const r=el.getBoundingClientRect(),l=el.querySelector('.toggle-lever'),s=el.querySelector('span:last-child').getBoundingClientRect();const c=getComputedStyle(l.querySelector('.red-paddle'));return {box:[r.x+scrollX,r.y+scrollY,r.width,r.height],label:[s.x+scrollX,s.y+scrollY,s.width,s.height],tilt:c.transform,paint:c.backgroundImage}}""")
            off=switch_shape();r=page.locator('#power').bounding_box();page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);page.mouse.down();page.wait_for_timeout(120);pressed=switch_shape()
            assert off['box']==pressed['box'] and off['label']==pressed['label'] and off['tilt']!=pressed['tilt']
            page.mouse.up();page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.wait_for_timeout(120);on=switch_shape()
            assert on['box']==off['box'] and on['label']==off['label'] and on['tilt']!=off['tilt'] and '239, 89, 65' in on['paint'] and '215, 53, 35' in on['paint']
            page.focus('#power');page.keyboard.down('Space');during=switch_shape();assert during['box']==on['box'] and during['label']==on['label'];page.keyboard.up('Space');assert stopped()
            checks.append('power chassis and label immobile on pointer/keyboard; only red rocker tilts between off/press/on')
            widths=[]
            for width in [1200,1000,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                assert page.locator('.privacy,footer,#power-label').count()==0 and page.locator('#density-value').is_visible()
                sizes=page.evaluate("""()=>{const k=document.querySelector('.buttons').getBoundingClientRect(),c=document.querySelector('.control-column').getBoundingClientRect();return {widths:[...document.querySelectorAll('.buttons button')].map(e=>e.getBoundingClientRect().width),gap:k.left-c.right,overflow:document.documentElement.scrollWidth>innerWidth}}""")
                widths.append(sizes['widths']);assert not sizes['overflow'] and (sizes['gap']>10 or width<=900)
            assert all(abs(a/b-widths[0][0]/widths[1][0])<.01 for a,b in zip(widths[0],widths[1])) and all(w>=44 for w in widths[2])
            checks.append('selected display text removed and keycaps fixed-width at desktop sizes without mobile overflow')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                deck=page.evaluate("""()=>{const c=document.querySelector('.density-control').getBoundingClientRect(),l=document.querySelector('label[for=density]').getBoundingClientRect(),column=document.querySelector('.control-column'),d=document.querySelector('.control-panel');return {gap:(l.top-c.bottom)/(c.width/document.querySelector('.density-control').offsetWidth),border:getComputedStyle(column).borderTopWidth,background:getComputedStyle(d).backgroundImage,width:d.getBoundingClientRect().width}}""")
                assert deck['gap']>=8 and deck['border']=='0px' and deck['background']=='none'
            checks.append('independent edge-anchored controls with unboxed instrument column and density label clearance at desktop/mobile')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                anchor=page.evaluate("""()=>{const r=s=>document.querySelector(s).getBoundingClientRect(),b=r('.bezel'),c=r('.control-column'),k=r('.buttons'),p=r('#power'),l=r('#physical-led');return {left:Math.abs(c.left-b.left),right:Math.abs(k.right-b.right),bottom:Math.abs(c.bottom-k.bottom),led:Math.max(0,b.bottom-l.top)}}""")
                assert all(v<1 for name,v in anchor.items() if name not in (['bottom'] if width<=600 else [])),anchor
            checks.append('independent controls anchor exact left/right case edges and shared bottom with LED outside lower bezel')
            fresh();page.locator('#power').scroll_into_view_if_needed()
            def hinge():
                return page.locator('.toggle-lever').evaluate("""el=>{const r=el.querySelector('.paddle-root').getBoundingClientRect(),p=el.querySelector('.red-paddle').getBoundingClientRect();return {root:[r.x+r.width/2+scrollX,r.y+r.height/2+scrollY],cap:p.y+p.height/2+scrollY}}""")
            offhinge=hinge();assert offhinge['cap']>offhinge['root'][1]
            page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');page.wait_for_timeout(180);onhinge=hinge()
            assert all(abs(a-b)<.01 for a,b in zip(onhinge['root'],offhinge['root'])) and onhinge['cap']<onhinge['root'][1]
            checks.append('fixed paddle root with free red cap below when off and above when on')
            # CSS rotateX maps a downward local free end to positive Z for the full 35..145 degree path.
            import math
            assert all(23*math.sin(math.radians(a))>0 for a in range(35,146))
            paint=page.locator('.paddle-root').evaluate('el=>getComputedStyle(el).backgroundImage')
            assert '173, 41, 27' in paint and '213, 68, 45' in paint
            checks.append('integrated red pivot material and outward positive-Z paddle sweep through every intermediate angle')
            support=page.locator('.paddle-root').evaluate("""el=>{const r=el.getBoundingClientRect(),w=el.parentElement.getBoundingClientRect(),s=getComputedStyle(el);return {w:r.width,h:r.height,well:w.height,radius:s.borderRadius}}""")
            assert abs(support['h']/support['w']-53/25)<.01 and support['h']<support['well'] and support['radius']=='2px'
            checks.append('full-height red rectangular support replaces standalone oval without changing paddle motion')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                lamp=page.evaluate("""()=>{const r=s=>document.querySelector(s).getBoundingClientRect(),b=r('.bezel'),l=r('#physical-led'),c=r('.buttons');return {gap:l.top-b.bottom,inset:b.right-l.right,clear:l.bottom<c.top}}""")
                assert 10<=lamp['gap']<=21 and abs(lamp['inset'])<1 and lamp['clear'],lamp
            checks.append('monitor lamp sits outside lower-right bezel on shell without overlapping controls at desktop/mobile')
            fresh();page.focus('#density');page.keyboard.press('End');assert page.inner_text('#boot-density')=='160' and page.evaluate('calls')==0
            assert page.locator('.scale-mark').count()==11 and page.locator('.scale-number.min').text_content()=='40' and page.locator('.scale-number.max').text_content()=='160'
            style=page.evaluate("""()=>{const s=id=>getComputedStyle(document.querySelector(id));return {led:s('#physical-led').borderTopWidth,capture:s('#capture').backgroundImage,save:s('#save').color,copy:s('#copy').color,plate:getComputedStyle(document.querySelector('.density-track'),'::before').backgroundImage}}""")
            assert style['led']=='0px' and '239, 173, 97' in style['capture'] and style['save']==style['copy'] and style['plate']=='none'
            checks.append('orange capture ivory copy/save unringed lamp and open engraved scale; off density updates boot without media')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                for value in [40,96,160]:
                    page.locator('#density').evaluate('(el,v)=>{el.value=v;el.dispatchEvent(new Event("input"))}',value)
                    angle=page.evaluate("""()=>{const a=document.querySelector('#density').getBoundingClientRect(),d=document.querySelector('.knob-dot').getBoundingClientRect();return Math.atan2(d.x+d.width/2-a.x-a.width/2,-(d.y+d.height/2-a.y-a.height/2))*180/Math.PI}""")
                    assert abs(angle-(-135+(value-40)/120*270))<1,(width,value,angle)
            checks.append('rotating dot matches shared scale angles at min/default/max on desktop/mobile')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                align=page.evaluate("""()=>{const p=document.querySelector('.power-engraving').getBoundingClientRect(),d=document.querySelector('label[for=density]').getBoundingClientRect(),g=getComputedStyle(document.querySelector('.knob-dot-arm'));return {baseline:Math.abs(p.bottom-d.bottom),grip:[parseFloat(g.width),parseFloat(g.height)]}}""")
                assert align['baseline']<1 and align['grip'][1]>align['grip'][0],align
            checks.append('POWER engraving baseline matches DENSITY; raised grip long axis follows rotating dot')
            for width in [1200,400]:
                page.set_viewport_size({'width':width,'height':900});fresh()
                for value in [40,96,160]:
                    page.locator('#density').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input"))}',value)
                    page.locator('#density').scroll_into_view_if_needed()
                    dot=page.locator('.knob-dot').bounding_box();shot=page.screenshot()
                    import base64
                    contrast=page.evaluate("""async arg=>{const i=new Image();i.src='data:image/png;base64,'+arg.b;await i.decode();const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);const d=x.getImageData(Math.floor(arg.x),Math.floor(arg.y),1,1).data;return [...d]}""",{'b':base64.b64encode(shot).decode('ascii'),'x':dot['x']+dot['width']/2,'y':dot['y']+dot['height']/2})
                    assert 90<min(contrast[:3]) and max(contrast[:3])<170,(width,value,contrast)
            checks.append('rendered inset dot remains visibly muted gray on raised rotating grip at min/default/max desktop/mobile')
            stability=[]
            for w,h in [(1920,1080),(1680,898),(390,844)]:
                page.set_viewport_size({'width':w,'height':h});fresh();page.wait_for_timeout(150)
                def shape():
                    return page.evaluate("""()=>{const r=document.querySelector('.machine').getBoundingClientRect(),b=document.querySelector('.bezel').getBoundingClientRect();return {w:r.width,h:r.height,x:r.x,y:r.y,bw:b.width,bh:b.height,overflow:document.documentElement.scrollWidth>innerWidth}}""")
                idle=shape();page.click('#power');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');live=shape();page.click('#capture');frozen=shape()
                assert all(abs(idle[k]-v[k])<1 for v in [live,frozen] for k in ['w','h','bw','bh']), (w,idle,live,frozen)
                assert not live['overflow'] and idle['x']>=0 and idle['y']>=0
                if w>600:assert idle['y']+idle['h']+20<=h
                stability.append({'viewport':[w,h],'idle':idle,'live':live,'frozen':frozen})
            checks.append('machine and bezel dimensions stable idle/live/frozen at 1920x1080 1680x898 and 390x844')
            fresh();page.click('#capture');page.wait_for_function('document.querySelector("#status").textContent.includes("Live ASCII targets")');assert page.evaluate('calls')==1 and page.locator('#power').get_attribute('aria-checked')=='true'
            page.click('#capture');assert page.locator('#physical-led').get_attribute('data-state')=='captured' and page.evaluate('calls')==1
            checks.append('deliberate Capture while off opens camera once then next Capture freezes')
            fresh('pending');page.click('#capture');page.wait_for_function('window.release!==undefined');page.click('#capture');assert page.evaluate('calls')==1;page.click('#power');page.evaluate('release()');page.wait_for_function('streams.every(s=>s.getTracks()[0].readyState==="ended")')
            checks.append('repeated Capture during opening never duplicates request and power cancels safely')
            fresh();page.locator('#density').scroll_into_view_if_needed();r=page.locator('#density').bounding_box();page.mouse.move(r['x']+r['width']/2,r['y']+r['height']/2);page.mouse.down();page.mouse.move(r['x']+r['width']/2+40,r['y']+r['height']/2,steps=5);page.mouse.up()
            assert page.locator('#density').input_value()=='120' and page.evaluate('calls')==0
            page.focus('#density');page.keyboard.press('ArrowRight');assert page.locator('#density').input_value()=='128'
            checks.append('40px pointer drag changes density by24 at60percent gain; keyboard retains8step')
            fresh();lighting=[];grips=[]
            for value in [40,96,160]:
                page.locator('#density').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input"))}',value)
                lighting.append(page.locator('.density-track').evaluate("el=>{const s=getComputedStyle(el,'::after');return [s.transform,s.backgroundImage,s.boxShadow]}"))
                grips.append(page.locator('.knob-dot-arm').evaluate('el=>getComputedStyle(el).transform'))
            assert lighting[0]==lighting[1]==lighting[2] and len(set(grips))==3
            checks.append('knob body lighting and cast shadow stay world-fixed while grip and dot rotate')
            assert not errors, errors
            assert not external, external
            checks.append('no page errors or external requests')
            browser.close()
        print(json.dumps({'passed':len(checks),'viewportStability':stability,'syntheticLiveMetrics':metrics,'checks':checks}, ensure_ascii=True, indent=2))
    finally:
        server.terminate()
        server.wait(timeout=5)


if __name__ == '__main__':
    main()
