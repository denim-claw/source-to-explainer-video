// SPDX-License-Identifier: MIT
// Original minimal settings and props. See repository LICENSE.
export function setKit(T){
 const mat=c=>new T.MeshStandardMaterial({color:c,roughness:.92});
 function box(parent,w,h,d,x,y,z,color){const o=new T.Mesh(new T.BoxGeometry(w,h,d),mat(color));o.position.set(x,y,z);o.castShadow=true;o.receiveShadow=true;parent.add(o);return o;}
 function court(){const root=new T.Group();root.name='court';box(root,10,.12,6,0,-.09,0,'#182633');
  box(root,3.4,.16,1.5,-2.5,.05,-1.3,'#243C4A');box(root,2.8,.16,1.3,-2.5,.2,-1.5,'#2C4654');
  for(const x of [-4.35,4.35])for(const z of [-2.2,.8]){const p=new T.Mesh(new T.CylinderGeometry(.16,.2,3.25,16),mat('#304858'));p.position.set(x,1.56,z);root.add(p);box(root,.52,.15,.52,x,3.2,z,'#395466');}
  for(const x of [-2,0,2])box(root,1.1,2.5,.14,x,1.55,-2.8,'#203745');
  return root;
 }
 function throne(){const root=new T.Group();root.name='throne';box(root,.8,.14,.75,0,.62,0,'#395466');box(root,.85,1.35,.12,0,1.12,-.32,'#395466');for(const x of [-.38,.38]){box(root,.09,.7,.09,x,.3,.23,'#395466');box(root,.1,.14,.7,x,.95,0,'#7A7455');}return root;}
 function chest(){const root=new T.Group();root.name='property-chest';box(root,.64,.38,.45,0,.2,0,'#8D7655');box(root,.68,.1,.48,0,.44,0,'#A08B65');for(const x of [-.22,.22])box(root,.035,.46,.47,x,.23,0,'#3A4D58');box(root,.08,.1,.02,0,.30,.24,'#BFB18C');return root;}
 function meetingRoom(){const root=new T.Group();root.name='meeting-room';box(root,8,.1,5,0,-.1,0,'#182633');box(root,3,.13,1.25,0,.86,0,'#395466');for(const x of [-1.2,1.2])for(const z of [-.42,.42])box(root,.08,.85,.08,x,.4,z,'#526B79');return root;}
 function house({wallColor='#7F9CA8',roofColor='#465765'}={}){
  const root=new T.Group();root.name='house';
  box(root,1.5,1.3,1.2,0,.65,0,wallColor);
  const roof=new T.Mesh(new T.ConeGeometry(1.2,.7,4),mat(roofColor));
  roof.name='roof';roof.position.y=1.65;roof.rotation.y=Math.PI/4;root.add(roof);
  box(root,.25,.7,.025,0,.35,.614,'#263444');
  for(const x of [-.46,.46])box(root,.25,.24,.03,x,.85,.616,'#E4CE9E');
  return root;
 }
 return {court,throne,chest,meetingRoom,house};
}
