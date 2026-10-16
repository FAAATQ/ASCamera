import test from 'node:test';
import assert from 'node:assert/strict';
import {dimensions,luminance,toAscii,RAMP} from '../ascii.js';
test('black and white map to ramp endpoints',()=>assert.equal(toAscii([0,0,0,255,255,255,255,255],2,1),' @'));
test('weighted luminance prioritises green',()=>assert.ok(luminance(0,255,0)>luminance(255,0,0)));
test('transparent pixels composite onto black',()=>assert.equal(toAscii([255,255,255,0],1,1),' '));
test('monospace aspect correction',()=>assert.deepEqual(dimensions(640,480,96),{columns:96,rows:36}));
test('density clamped and defaulted',()=>{assert.equal(dimensions(1,1,-9).columns,40);assert.equal(dimensions(1,1,999).columns,160);assert.equal(dimensions(1,1,NaN).columns,96);});
test('invalid dimensions rejected',()=>assert.throws(()=>dimensions(0,1,96),RangeError));
test('invalid buffer and ramp rejected',()=>{assert.throws(()=>toAscii([],1,1),RangeError);assert.throws(()=>toAscii([0,0,0,255],1,1,''),RangeError);});
test('line counts lengths and deterministic mapping',()=>{const a=new Uint8ClampedArray(4*6).fill(255);assert.equal(toAscii(a,3,2),'@@@\n@@@');assert.equal(toAscii(a,3,2),toAscii(a,3,2));assert.equal(RAMP.length,10);});

test('measured cell aspect controls rows across orientations and density',()=>{for(const [w,h] of [[640,480],[960,540],[480,640],[540,960]])for(const density of [40,96,160]){const {columns,rows}=dimensions(w,h,density,9.6328125/20);assert.equal(columns,density);assert.ok(Math.abs(rows-columns*h/w*9.6328125/20)<=0.5);}});

import {crtPoint} from '../crt.js';
test('CRT mesh bows edges and preserves full source bounds',()=>{for(let y=0;y<=100;y++)for(let x=0;x<=100;x++){const p=crtPoint(x/100,y/100);assert.ok(p.x>0&&p.x<1&&p.y>0&&p.y<1);}assert.ok(crtPoint(0,0).y-crtPoint(.5,0).y>.08);assert.deepEqual(crtPoint(.5,.5),{x:.5,y:.5});});
