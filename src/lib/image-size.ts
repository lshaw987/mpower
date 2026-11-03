import { readFileSync } from 'node:fs';
import { join } from 'node:path';

/**
 * Build-time JPEG dimensions for a file under public/ (e.g. "/images/resources/x.jpg"),
 * so <img> tags can carry honest width/height and the layout never shifts while a
 * photo loads. Reads the SOF marker only. Returns null for anything it can't read.
 */
export function jpegSize(publicPath: string): { width: number; height: number } | null {
  try {
    const buf = readFileSync(join(process.cwd(), 'public', publicPath));
    if (buf[0] !== 0xff || buf[1] !== 0xd8) return null;
    const SOF = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);
    let i = 2;
    while (i + 9 < buf.length) {
      if (buf[i] !== 0xff) { i++; continue; }
      const marker = buf[i + 1];
      if (marker === 0xff) { i++; continue; }
      if (marker === 0x01 || (marker >= 0xd0 && marker <= 0xd8)) { i += 2; continue; }
      const len = buf.readUInt16BE(i + 2);
      if (SOF.has(marker)) return { height: buf.readUInt16BE(i + 5), width: buf.readUInt16BE(i + 7) };
      i += 2 + len;
    }
  } catch {
    /* fall through */
  }
  return null;
}
