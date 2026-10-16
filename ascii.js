export const RAMP = ' .:-=+*#%@';
export function dimensions(width, height, density, cellAspect = 0.5) {
  if (!(width > 0 && height > 0 && Number.isFinite(width + height))) throw new RangeError('Invalid image size');
  const columns = Math.round(Math.max(40, Math.min(160, Number(density) || 96)));
  return {columns, rows: Math.max(1, Math.round(columns * height / width * cellAspect))};
}
export function luminance(r, g, b) { return 0.2126*r + 0.7152*g + 0.0722*b; }
export function toAscii(data, width, height, ramp = RAMP) {
  if (!ramp.length || !Number.isInteger(width) || !Number.isInteger(height) || width < 1 || height < 1 || data.length !== width*height*4) throw new RangeError('Invalid pixel buffer');
  const lines = [];
  for (let y=0;y<height;y++) {
    let line='';
    for(let x=0;x<width;x++) { const i=(y*width+x)*4; const light=luminance(data[i],data[i+1],data[i+2])*(data[i+3]/255); line += ramp[Math.round(Math.max(0,Math.min(255,light))/255*(ramp.length-1))]; }
    lines.push(line);
  }
  return lines.join('\n');
}
