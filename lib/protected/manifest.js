// written by v2/build_site.py: the paid files the /p function serves (path under /p/ -> [gzipped body, type, level needed])
import f0 from './f0.bin';
import f1 from './f1.bin';
import f2 from './f2.bin';
export const FILES = {
  "t1/5b3223712549d431/data.json": [f0, "application/json; charset=utf-8", 1],
  "t2/a21cba01103015c2/final.js": [f1, "application/javascript; charset=utf-8", 2],
  "t2/a21cba01103015c2/brain.js": [f2, "application/javascript; charset=utf-8", 2],
};
