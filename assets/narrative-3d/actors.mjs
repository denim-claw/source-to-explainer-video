// SPDX-License-Identifier: MIT
// Original articulated actor kit. See repository LICENSE.
// Coordinates: +Y up, face +Z; root at floor. No textures or remote dependencies.
export function actorKit(T){
 const m=c=>new T.MeshStandardMaterial({color:c,roughness:.87,metalness:0});
 function mesh(parent,geo,mat,x=0,y=0,z=0){const o=new T.Mesh(geo,mat);o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
 const capsule=(r,len)=>new T.CapsuleGeometry(r,Math.max(.01,len-2*r),6,12);
 function actor({role='courtier',color='#7CAFF2',skin='#CFD8DF'}={}){
  const root=new T.Group();root.name=role;const body=new T.Group();root.add(body);
  const coat=m(color),flesh=m(skin),dark=m('#263444'),trim=m('#F3CE62');
  mesh(body,new T.CylinderGeometry(.19,.25,.55,16),coat,0,1.1,0);
  mesh(body,new T.SphereGeometry(.22,24,16),flesh,0,1.67,0).scale.set(.86,1.08,.92);
  mesh(body,new T.CylinderGeometry(.07,.08,.12,12),flesh,0,1.43,0);
  // A face cue makes a turn/departure readable without labels.
  mesh(body,new T.BoxGeometry(.29,.09,.022),dark,0,1.70,.194);
  for(const x of [-.07,.07])mesh(body,new T.BoxGeometry(.044,.024,.012),trim,x,1.70,.211);
  const joints={};
  for(const side of [-1,1]){
   const key=side<0?'L':'R';
   const shoulder=new T.Group();shoulder.position.set(side*.26,1.3,0);body.add(shoulder);
   mesh(shoulder,capsule(.075,.36),coat,0,-.16,0);
   const elbow=new T.Group();elbow.position.y=-.34;shoulder.add(elbow);
   mesh(elbow,capsule(.063,.33),coat,0,-.145,0);mesh(elbow,new T.SphereGeometry(.075,12,10),flesh,0,-.33,0);
   const hip=new T.Group();hip.position.set(side*.12,.85,0);body.add(hip);
   mesh(hip,capsule(.09,.43),dark,0,-.2,0);
   const knee=new T.Group();knee.position.y=-.4;hip.add(knee);
   mesh(knee,capsule(.073,.40),dark,0,-.18,0);
   const foot=mesh(knee,new T.BoxGeometry(.17,.12,.29),dark,0,-.39,.055);
   joints['arm'+key]=shoulder;joints['elbow'+key]=elbow;joints['leg'+key]=hip;joints['knee'+key]=knee;joints['foot'+key]=foot;
  }
  if(role==='ruler'){
   const crown=new T.Group();crown.position.y=1.88;body.add(crown);
   mesh(crown,new T.CylinderGeometry(.21,.2,.10,16),trim);
   for(let i=0;i<5;i++){let a=i*Math.PI*2/5;mesh(crown,new T.ConeGeometry(.04,.14,4),trim,Math.sin(a)*.18,.09,Math.cos(a)*.18);}
   mesh(body,new T.CylinderGeometry(.25,.32,.86,16,1,true,Math.PI*.55,Math.PI*.9),m('#315C67'),0,.99,-.06);
  }
  if(role==='guard'){
   mesh(body,new T.SphereGeometry(.235,16,12,0,Math.PI*2,0,Math.PI*.56),m('#6F8292'),0,1.72,0);
   mesh(body,new T.BoxGeometry(.38,.36,.12),m('#526B79'),0,1.14,.16);
  }
  function pose({walk=0,phase=0,bow=0,reach=0,stop=0,recoil=0}={}){
   if(![walk,phase,bow,reach,stop,recoil].every(Number.isFinite))throw new TypeError('Actor pose values must be finite');
   [walk,bow,reach,stop,recoil]=[walk,bow,reach,stop,recoil].map(n=>Math.max(0,Math.min(1,n)));
   body.position.y=0;body.rotation.set(bow*.62,0,0);
   for(const s of [-1,1]){const k=s<0?'L':'R',swing=Math.sin(phase+(s<0?0:Math.PI))*walk;
    joints['leg'+k].rotation.set(swing*.48,0,0);joints['knee'+k].rotation.x=Math.max(0,-swing)*.58;
    joints['arm'+k].rotation.set(-swing*.32,0,s*.05);joints['elbow'+k].rotation.set(-.1,0,0);
   }
   joints.armR.rotation.x-=reach*1.18+stop*1.48;
   joints.armR.rotation.z-=stop*.13;
   joints.elbowR.rotation.x-=reach*.3;
   body.rotation.x-=recoil*.1;
   return root;
  }
  pose();return {root,body,joints,pose};
 }
 return {actor};
}
