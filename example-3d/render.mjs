// SPDX-License-Identifier: MIT
// Local deterministic Three.js + Puppeteer renderer. No hosted API or narration.
import {createAssetServer} from './static-server.mjs';
import {readFile,writeFile,mkdir,stat} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {spawn,spawnSync,execFileSync} from 'node:child_process';
import {once} from 'node:events';
import assert from 'node:assert/strict';
import puppeteer from 'puppeteer-core';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2),proofOnly=args.includes('--proof'),noSandbox=args.includes('--no-sandbox');
const argIndex=args.indexOf('--output');
if(argIndex>=0&&!args[argIndex+1])throw Error('--output requires a path');
const out=path.resolve(ROOT,argIndex>=0?args[argIndex+1]:'example-3d/out/kit.mp4');
const outputDir=proofOnly?path.join(ROOT,'example-3d/out'):path.dirname(out);
if(!proofOnly&&existsSync(out))throw Error('Refusing to overwrite an existing master; use --output with a new filename');
await mkdir(outputDir,{recursive:true});
const hash=b=>createHash('sha256').update(b).digest('hex');
const jsonWrite=(p,x)=>writeFile(p,JSON.stringify(x,null,2)+'\n');
const server=await createAssetServer(ROOT);
await new Promise(r=>server.listen(0,'127.0.0.1',r));
const origin=`http://127.0.0.1:${server.address().port}`;
let browser,encoder;
try{
 const chrome=process.env.CHROMIUM_PATH||'/usr/bin/chromium';
 const launchArgs=['--enable-unsafe-swiftshader','--use-angle=swiftshader','--disable-dev-shm-usage','--disable-background-networking'];
 if(noSandbox)launchArgs.push('--no-sandbox');
 browser=await puppeteer.launch({executablePath:chrome,headless:true,args:launchArgs});
 const page=await browser.newPage();await page.setViewport({width:1280,height:720,deviceScaleFactor:1});
 const errors=[],externalRequests=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.setRequestInterception(true);
 page.on('request',req=>{if(req.url().startsWith(origin+'/')||req.url().startsWith('data:'))req.continue();else{externalRequests.push(new URL(req.url()).origin);req.abort();}});
 await page.goto(origin+'/example-3d/',{waitUntil:'networkidle0'});
 const ready=await page.evaluate(()=>window.assetReady);assert.deepEqual({...ready},{three:'186',textures:4,shots:3});
 const times=[0,.9,3.9,4,4.08,4.17,4.4,5.5,7.9,8,8.08,8.17,8.4,10,11.9];
 const forward=new Map(),cameras=new Map(),labelChecks=[],framingChecks=[];
 for(const t of times){
  const info=await page.evaluate(t=>window.renderAt(t),t),labels=await page.evaluate(()=>window.inspectLabels());
  assert.equal(labels.clipped.length,0,'DOM label clipping');assert.equal(labels.overlaps.length,0,'DOM label overlap');
  if(cameras.has(info.shot))assert.equal(cameras.get(info.shot),info.camera,'camera changed inside shot');else cameras.set(info.shot,info.camera);
  const bytes=await page.screenshot({type:'png'});forward.set(t,hash(bytes));labelChecks.push({time:t,labels:labels.nodes.length});assert.ok(info.visibleFoci>0);assert.deepEqual(info.framingFailures,[]);framingChecks.push({time:t,visibleFoci:info.visibleFoci});
 }
 for(const t of [...times].reverse()){
  await page.evaluate(t=>window.renderAt(t),t);assert.equal(hash(await page.screenshot({type:'png'})),forward.get(t),`reverse seek mismatch at ${t}`);
 }
 assert.equal(new Set([0,4,8].map(t=>forward.get(t))).size,3,'Shots must have distinct first-frame pixels');assert.deepEqual(errors,[]);assert.deepEqual(externalRequests,[]);
 const proof={status:'pass',scope:'same-browser PNG forward/reverse seeking; not cross-GPU equality or source/narration review',times,textureCount:ready.textures,shots:ready.shots,cameraSignatures:[...cameras].map(([shot,s])=>({shot,sha256:hash(s)})),labelChecks,framingChecks,labelAuditScope:'four DOM labels: viewport containment and pairwise DOM intersections only',frameHashes:Object.fromEntries(forward),externalRequests:externalRequests.length};
 await jsonWrite(path.join(outputDir,'browser-proof.json'),proof);
 console.log(JSON.stringify({browserProof:'pass',times:times.length,textures:ready.textures,shots:ready.shots}));
 if(!proofOnly){
  const ffargs=['-v','error','-n','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart','-threads','2',out];
  encoder=spawn('ffmpeg',ffargs,{stdio:['pipe','ignore','pipe']});let stderr='';encoder.stderr.on('data',b=>stderr+=b.toString());
  let pipeError=null;encoder.stdin.on('error',e=>pipeError=e);const finished=once(encoder,'close');finished.catch(()=>{});
  for(let n=0;n<360;n++){
   await page.evaluate(t=>window.renderAt(t),n/30);const bytes=await page.screenshot({type:'jpeg',quality:95});
   if(pipeError||encoder.exitCode!==null)throw Error(`ffmpeg terminated during input: ${stderr}`);
   if(!encoder.stdin.write(bytes))await Promise.race([once(encoder.stdin,'drain'),finished.then(()=>{throw Error(`ffmpeg terminated during input: ${stderr}`);})]);
   if(n%120===119)console.log(`rendered ${n+1}/360`);
  }
  encoder.stdin.end();const [code]=await finished;if(code!==0)throw Error(`ffmpeg failed: ${stderr}`);
  assert.deepEqual(errors,[]);assert.deepEqual(externalRequests,[]);
  const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',out],{encoding:'utf8'}));
  const video=probe.streams.filter(s=>s.codec_type==='video'),audio=probe.streams.filter(s=>s.codec_type==='audio');
  assert.equal(video.length,1);assert.equal(audio.length,0);const v=video[0];assert.equal(v.codec_name,'h264');assert.equal(v.width,1280);assert.equal(v.height,720);assert.equal(v.nb_read_frames,'360');assert.equal(v.avg_frame_rate,'30/1');assert.ok(Math.abs(Number(probe.format.duration)-12)<.001);
  const decode=spawnSync('ffmpeg',['-v','error','-i',out,'-f','null','-'],{encoding:'utf8',stdio:['ignore','pipe','pipe']});assert.equal(decode.status,0,'full decode exit');assert.equal(decode.stderr,'','full decode error output');
  const frames=[45,105,120,125,165,225,240,252,345],filter=`select='${frames.map(n=>`eq(n,${n})`).join('+')}',scale=426:240,tile=3x3`;
  const contact=path.join(outputDir,'contact.jpg');execFileSync('ffmpeg',['-v','error','-y','-i',out,'-vf',filter,'-frames:v','1','-q:v','2',contact]);
  const sourceFiles=['package-lock.json','example-3d/scene.mjs','example-3d/render.mjs','example-3d/static-server.mjs','example-3d/index.html','assets/hybrid-3d/animals.mjs','assets/hybrid-3d/fixed-shot.mjs','assets/hybrid-3d/fx-flipbook.mjs','assets/narrative-3d/actors.mjs','assets/narrative-3d/sets.mjs','assets/hybrid-3d/textures/manifest.json'];
  const sources={};for(const file of sourceFiles)sources[file]=hash(await readFile(path.join(ROOT,file)));
  const report={status:'technical-pass',createdUTC:new Date().toISOString(),kind:'original silent asset demo',master:{file:path.basename(out),sha256:hash(await readFile(out)),bytes:(await stat(out)).size,duration:Number(probe.format.duration),width:v.width,height:v.height,fps:v.avg_frame_rate,frames:Number(v.nb_read_frames),audioStreams:0,fullDecode:'pass'},contact:{file:'contact.jpg',sha256:hash(await readFile(contact)),extractedFrameIndices:frames,sampleTimes:frames.map(n=>n/30)},browserProof:proof,sources,tools:{node:process.version,chromium:execFileSync(chrome,['--version'],{encoding:'utf8'}).trim(),three:'0.186.1',puppeteerCore:'25.14.0'},sandboxDisabled:noSandbox,notEstablished:['narration/caption sync','full-source coverage','historical fidelity','photorealism','IK/foot locking','human full-film review','cross-machine pixel identity']};
  await jsonWrite(path.join(outputDir,'verification.json'),report);console.log(JSON.stringify(report.master));
 }
}finally{
 if(encoder?.exitCode===null)encoder.kill('SIGTERM');
 if(browser)await browser.close();await new Promise(r=>server.close(r));
}
