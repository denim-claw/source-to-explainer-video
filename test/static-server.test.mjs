// SPDX-License-Identifier: MIT
import test from 'node:test';import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,symlink,rm} from 'node:fs/promises';
import os from 'node:os';import path from 'node:path';import http from 'node:http';
import {createAssetServer} from '../example-3d/static-server.mjs';
async function fixture(t){
 const root=await mkdtemp(path.join(os.tmpdir(),'3d-static-fixture-'));
 for(const p of ['assets','example-3d','node_modules/three/build'])await mkdir(path.join(root,p),{recursive:true});
 await writeFile(path.join(root,'LICENSE'),'PRIVATE_ROOT_FIXTURE');
 await writeFile(path.join(root,'.env'),'NOT_A_CREDENTIAL=PRIVATE_FIXTURE');
 await writeFile(path.join(root,'assets','public.txt'),'public asset');
 await writeFile(path.join(root,'example-3d','index.html'),'<title>public demo</title>');
 await writeFile(path.join(root,'node_modules/three/build','three.module.js'),'export const fixture=true;');
 const server=await createAssetServer(root);await new Promise(r=>server.listen(0,'127.0.0.1',r));
 t.after(async()=>{await new Promise(r=>server.close(r));await rm(root,{recursive:true,force:true});});
 const get=(uri,method='GET')=>new Promise((resolve,reject)=>{const req=http.request({host:'127.0.0.1',port:server.address().port,path:uri,method},res=>{let body='';res.on('data',b=>body+=b);res.on('end',()=>resolve({status:res.statusCode,body,headers:res.headers}));});req.on('error',reject);req.end();});
 return {root,get};
}
test('serves only intended assets/module/page; HEAD is bodyless',async t=>{
 const {get}=await fixture(t);assert.equal((await get('/assets/public.txt')).body,'public asset');
 assert.equal((await get('/example-3d/')).status,200);assert.equal((await get('/node_modules/three/build/three.module.js')).status,200);
 const head=await get('/assets/public.txt','HEAD');assert.equal(head.status,200);assert.equal(head.body,'');assert.equal(head.headers['x-content-type-options'],'nosniff');
 assert.equal((await get('/assets/public.txt','POST')).status,405);
});
test('encoded traversal and double encoding cannot read repository-private files',async t=>{
 const {get}=await fixture(t);
 for(const uri of ['/LICENSE','/.env','/assets/%2e%2e%2fLICENSE','/assets/%2E%2E%2FLICENSE','/assets/%2e%2e%2f.env','/example-3d/%2e%2e%2f.env','/node_modules/three/build/%2e%2e%2f%2e%2e%2f%2e%2e%2f.env','/assets/%252e%252e%252f.env','/assets/%00','/assets/%zz'])assert.equal((await get(uri)).status,404,uri);
});
test('symlinks cannot enlarge the allowlisted filesystem subtree',async t=>{
 const {root,get}=await fixture(t);
 await symlink(path.join(root,'.env'),path.join(root,'assets','private.txt'));
 await symlink(root,path.join(root,'assets','escape'));
 await symlink(path.join(root,'assets','public.txt'),path.join(root,'assets','inside.txt'));
 assert.equal((await get('/assets/private.txt')).status,404);assert.equal((await get('/assets/escape/.env')).status,404);assert.equal((await get('/assets/inside.txt')).body,'public asset');
});
