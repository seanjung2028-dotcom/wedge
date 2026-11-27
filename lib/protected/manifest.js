// written by v2/build_site.py: the paid files the /p function serves (path under /p/ -> [gzipped body, type, level needed])
import f0 from './f0.bin';
import f1 from './f1.bin';
import f2 from './f2.bin';
export const FILES = {
  "t1/38e61850d981ef4b/data.json": [f0, "application/json; charset=utf-8", 1],
  "t2/8602acc1ca2188b5/final.js": [f1, "application/javascript; charset=utf-8", 2],
  "t2/8602acc1ca2188b5/brain.js": [f2, "application/javascript; charset=utf-8", 2],
};
