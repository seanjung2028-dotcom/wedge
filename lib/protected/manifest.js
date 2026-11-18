// written by v2/build_site.py: the paid files the /p function serves (path under /p/ -> [gzipped body, type, level needed])
import f0 from './f0.bin';
import f1 from './f1.bin';
import f2 from './f2.bin';
export const FILES = {
  "t1/c9f0dd74e6dc415d/data.json": [f0, "application/json; charset=utf-8", 1],
  "t2/b0cdfafb7cb28f26/final.js": [f1, "application/javascript; charset=utf-8", 2],
  "t2/b0cdfafb7cb28f26/brain.js": [f2, "application/javascript; charset=utf-8", 2],
};
