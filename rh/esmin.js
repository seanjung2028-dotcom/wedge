const fs = require('fs'); const esbuild = require('/opt/npm-tools/node_modules/esbuild');
const [,, inp, out] = process.argv;
let html = fs.readFileSync(inp, 'utf8');
html = html.replace(/<script>([\s\S]*?)<\/script>/g, (m, js) => '<script>' + esbuild.transformSync(js, { minify: true, loader: 'js', target: 'es2020' }).code.trim() + '</script>');
html = html.replace(/<style>([\s\S]*?)<\/style>/g, (m, css) => '<style>' + esbuild.transformSync(css, { minify: true, loader: 'css' }).code.trim() + '</style>');
fs.writeFileSync(out, html);
console.log('in', Buffer.byteLength(fs.readFileSync(inp, 'utf8')), 'out', Buffer.byteLength(html));
