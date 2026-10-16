// Static barrel mesh: the 10% corner guard band keeps every source corner inside the frame.
export function crtPoint(u,v){const x=2*u-1,y=2*v-1;const k=.22;return {x:.5+.40*x*(1+k*(1-y*y)),y:.5+.40*y*(1+k*(1-x*x))};}
export function paintCRT(ctx,source,width,height){
 ctx.fillStyle='#08160f';ctx.fillRect(0,0,width,height);
 const nx=16,ny=12;
 function triangle(a,b,c){
  const sx=a.u*source.width,sy=a.v*source.height;
  const bx=(b.u-a.u)*source.width,by=(b.v-a.v)*source.height,cx=(c.u-a.u)*source.width,cy=(c.v-a.v)*source.height;
  const det=bx*cy-by*cx;
  const A=((b.x-a.x)*cy-(c.x-a.x)*by)/det,B=((b.y-a.y)*cy-(c.y-a.y)*by)/det;
  const C=((c.x-a.x)*bx-(b.x-a.x)*cx)/det,D=((c.y-a.y)*bx-(b.y-a.y)*cx)/det;
  ctx.save();ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.lineTo(c.x,c.y);ctx.closePath();ctx.clip();ctx.transform(A,B,C,D,a.x-A*sx-C*sy,a.y-B*sx-D*sy);ctx.drawImage(source,0,0);ctx.restore();
 }
 const points=Array.from({length:ny+1},(_,j)=>Array.from({length:nx+1},(_,i)=>{const u=i/nx,v=j/ny,p=crtPoint(u,v);return {u,v,x:p.x*width,y:p.y*height};}));
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const a=points[j][i],b=points[j][i+1],c=points[j+1][i],d=points[j+1][i+1];triangle(a,b,c);triangle(b,d,c);}
}
