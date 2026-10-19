// SPDX-License-Identifier: MIT
// Private loopback demo server; canonical filesystem containment is mandatory.
import http from 'node:http';
import path from 'node:path';
import {readFile,realpath,stat} from 'node:fs/promises';
const WEB_ROOTS=['/assets/','/example-3d/','/node_modules/three/build/'];
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.mjs':'text/javascript','.png':'image/png','.jpg':'image/jpeg','.json':'application/json','.txt':'text/plain; charset=utf-8','.mp4':'video/mp4'};
export async function createAssetServer(root){
 const canonicalRoot=await realpath(root);
 // Keep lexical whitelist boundaries under the canonical repository root.
 // Resolving an allowed directory's symlink must not enlarge its authority.
 const allowed=WEB_ROOTS.map(p=>path.resolve(canonicalRoot,'.'+p));
 return http.createServer(async(req,res)=>{
  try{
   if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405).end();return;}
   const name=decodeURIComponent(new URL(req.url,'http://127.0.0.1').pathname);
   if(!WEB_ROOTS.some(p=>name.startsWith(p))){res.writeHead(404).end();return;}
   const candidate=path.resolve(canonicalRoot,'.'+name+(name.endsWith('/')?'index.html':''));
   const target=await realpath(candidate);
   if(!allowed.some(dir=>target.startsWith(dir+path.sep))){res.writeHead(404).end();return;}
   if(!(await stat(target)).isFile()){res.writeHead(404).end();return;}
   const data=await readFile(target);
   res.writeHead(200,{'Content-Type':MIME[path.extname(target)]||'application/octet-stream','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'});
   res.end(req.method==='HEAD'?undefined:data);
  }catch{res.writeHead(404).end();}
 });
}
