var be=typeof globalThis<"u"?globalThis:typeof window<"u"?window:typeof global<"u"?global:typeof self<"u"?self:{};function te(n){return n&&n.__esModule&&Object.prototype.hasOwnProperty.call(n,"default")?n.default:n}function Me(n){if(Object.prototype.hasOwnProperty.call(n,"__esModule"))return n;var i=n.default;if(typeof i=="function"){var p=function y(){return this instanceof y?Reflect.construct(i,arguments,this.constructor):i.apply(this,arguments)};p.prototype=i.prototype}else p={};return Object.defineProperty(p,"__esModule",{value:!0}),Object.keys(n).forEach(function(y){var v=Object.getOwnPropertyDescriptor(n,y);Object.defineProperty(p,y,v.get?v:{enumerable:!0,get:function(){return n[y]}})}),p}var A={exports:{}},r={};/**
 * @license React
 * react.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */var B;function re(){if(B)return r;B=1;var n=Symbol.for("react.element"),i=Symbol.for("react.portal"),p=Symbol.for("react.fragment"),y=Symbol.for("react.strict_mode"),v=Symbol.for("react.profiler"),m=Symbol.for("react.provider"),S=Symbol.for("react.context"),x=Symbol.for("react.forward_ref"),$=Symbol.for("react.suspense"),C=Symbol.for("react.memo"),R=Symbol.for("react.lazy"),z=Symbol.iterator;function X(e){return e===null||typeof e!="object"?null:(e=z&&e[z]||e["@@iterator"],typeof e=="function"?e:null)}var q={isMounted:function(){return!1},enqueueForceUpdate:function(){},enqueueReplaceState:function(){},enqueueSetState:function(){}},L=Object.assign,I={};function _(e,t,o){this.props=e,this.context=t,this.refs=I,this.updater=o||q}_.prototype.isReactComponent={},_.prototype.setState=function(e,t){if(typeof e!="object"&&typeof e!="function"&&e!=null)throw Error("setState(...): takes an object of state variables to update or a function which returns an object of state variables.");this.updater.enqueueSetState(this,e,t,"setState")},_.prototype.forceUpdate=function(e){this.updater.enqueueForceUpdate(this,e,"forceUpdate")};function V(){}V.prototype=_.prototype;function E(e,t,o){this.props=e,this.context=t,this.refs=I,this.updater=o||q}var j=E.prototype=new V;j.constructor=E,L(j,_.prototype),j.isPureReactComponent=!0;var D=Array.isArray,U=Object.prototype.hasOwnProperty,O={current:null},H={key:!0,ref:!0,__self:!0,__source:!0};function T(e,t,o){var a,u={},c=null,f=null;if(t!=null)for(a in t.ref!==void 0&&(f=t.ref),t.key!==void 0&&(c=""+t.key),t)U.call(t,a)&&!H.hasOwnProperty(a)&&(u[a]=t[a]);var l=arguments.length-2;if(l===1)u.children=o;else if(1<l){for(var s=Array(l),k=0;k<l;k++)s[k]=arguments[k+2];u.children=s}if(e&&e.defaultProps)for(a in l=e.defaultProps,l)u[a]===void 0&&(u[a]=l[a]);return{$$typeof:n,type:e,key:c,ref:f,props:u,_owner:O.current}}function J(e,t){return{$$typeof:n,type:e.type,key:t,ref:e.ref,props:e.props,_owner:e._owner}}function P(e){return typeof e=="object"&&e!==null&&e.$$typeof===n}function Q(e){var t={"=":"=0",":":"=2"};return"$"+e.replace(/[=:]/g,function(o){return t[o]})}var F=/\/+/g;function N(e,t){return typeof e=="object"&&e!==null&&e.key!=null?Q(""+e.key):t.toString(36)}function b(e,t,o,a,u){var c=typeof e;(c==="undefined"||c==="boolean")&&(e=null);var f=!1;if(e===null)f=!0;else switch(c){case"string":case"number":f=!0;break;case"object":switch(e.$$typeof){case n:case i:f=!0}}if(f)return f=e,u=u(f),e=a===""?"."+N(f,0):a,D(u)?(o="",e!=null&&(o=e.replace(F,"$&/")+"/"),b(u,t,o,"",function(k){return k})):u!=null&&(P(u)&&(u=J(u,o+(!u.key||f&&f.key===u.key?"":(""+u.key).replace(F,"$&/")+"/")+e)),t.push(u)),1;if(f=0,a=a===""?".":a+":",D(e))for(var l=0;l<e.length;l++){c=e[l];var s=a+N(c,l);f+=b(c,t,o,s,u)}else if(s=X(e),typeof s=="function")for(e=s.call(e),l=0;!(c=e.next()).done;)c=c.value,s=a+N(c,l++),f+=b(c,t,o,s,u);else if(c==="object")throw t=String(e),Error("Objects are not valid as a React child (found: "+(t==="[object Object]"?"object with keys {"+Object.keys(e).join(", ")+"}":t)+"). If you meant to render a collection of children, use an array instead.");return f}function M(e,t,o){if(e==null)return e;var a=[],u=0;return b(e,a,"","",function(c){return t.call(o,c,u++)}),a}function Y(e){if(e._status===-1){var t=e._result;t=t(),t.then(function(o){(e._status===0||e._status===-1)&&(e._status=1,e._result=o)},function(o){(e._status===0||e._status===-1)&&(e._status=2,e._result=o)}),e._status===-1&&(e._status=0,e._result=t)}if(e._status===1)return e._result.default;throw e._result}var d={current:null},g={transition:null},ee={ReactCurrentDispatcher:d,ReactCurrentBatchConfig:g,ReactCurrentOwner:O};function W(){throw Error("act(...) is not supported in production builds of React.")}return r.Children={map:M,forEach:function(e,t,o){M(e,function(){t.apply(this,arguments)},o)},count:function(e){var t=0;return M(e,function(){t++}),t},toArray:function(e){return M(e,function(t){return t})||[]},only:function(e){if(!P(e))throw Error("React.Children.only expected to receive a single React element child.");return e}},r.Component=_,r.Fragment=p,r.Profiler=v,r.PureComponent=E,r.StrictMode=y,r.Suspense=$,r.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED=ee,r.act=W,r.cloneElement=function(e,t,o){if(e==null)throw Error("React.cloneElement(...): The argument must be a React element, but you passed "+e+".");var a=L({},e.props),u=e.key,c=e.ref,f=e._owner;if(t!=null){if(t.ref!==void 0&&(c=t.ref,f=O.current),t.key!==void 0&&(u=""+t.key),e.type&&e.type.defaultProps)var l=e.type.defaultProps;for(s in t)U.call(t,s)&&!H.hasOwnProperty(s)&&(a[s]=t[s]===void 0&&l!==void 0?l[s]:t[s])}var s=arguments.length-2;if(s===1)a.children=o;else if(1<s){l=Array(s);for(var k=0;k<s;k++)l[k]=arguments[k+2];a.children=l}return{$$typeof:n,type:e.type,key:u,ref:c,props:a,_owner:f}},r.createContext=function(e){return e={$$typeof:S,_currentValue:e,_currentValue2:e,_threadCount:0,Provider:null,Consumer:null,_defaultValue:null,_globalName:null},e.Provider={$$typeof:m,_context:e},e.Consumer=e},r.createElement=T,r.createFactory=function(e){var t=T.bind(null,e);return t.type=e,t},r.createRef=function(){return{current:null}},r.forwardRef=function(e){return{$$typeof:x,render:e}},r.isValidElement=P,r.lazy=function(e){return{$$typeof:R,_payload:{_status:-1,_result:e},_init:Y}},r.memo=function(e,t){return{$$typeof:C,type:e,compare:t===void 0?null:t}},r.startTransition=function(e){var t=g.transition;g.transition={};try{e()}finally{g.transition=t}},r.unstable_act=W,r.useCallback=function(e,t){return d.current.useCallback(e,t)},r.useContext=function(e){return d.current.useContext(e)},r.useDebugValue=function(){},r.useDeferredValue=function(e){return d.current.useDeferredValue(e)},r.useEffect=function(e,t){return d.current.useEffect(e,t)},r.useId=function(){return d.current.useId()},r.useImperativeHandle=function(e,t,o){return d.current.useImperativeHandle(e,t,o)},r.useInsertionEffect=function(e,t){return d.current.useInsertionEffect(e,t)},r.useLayoutEffect=function(e,t){return d.current.useLayoutEffect(e,t)},r.useMemo=function(e,t){return d.current.useMemo(e,t)},r.useReducer=function(e,t,o){return d.current.useReducer(e,t,o)},r.useRef=function(e){return d.current.useRef(e)},r.useState=function(e){return d.current.useState(e)},r.useSyncExternalStore=function(e,t,o){return d.current.useSyncExternalStore(e,t,o)},r.useTransition=function(){return d.current.useTransition()},r.version="18.3.1",r}var Z;function ne(){return Z||(Z=1,A.exports=re()),A.exports}var w=ne();const ge=te(w);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const oe=n=>n.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase(),ue=n=>n.replace(/^([A-Z])|[\s-_]+(\w)/g,(i,p,y)=>y?y.toUpperCase():p.toLowerCase()),G=n=>{const i=ue(n);return i.charAt(0).toUpperCase()+i.slice(1)},K=(...n)=>n.filter((i,p,y)=>!!i&&i.trim()!==""&&y.indexOf(i)===p).join(" ").trim(),ae=n=>{for(const i in n)if(i.startsWith("aria-")||i==="role"||i==="title")return!0};/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */var ie={xmlns:"http://www.w3.org/2000/svg",width:24,height:24,viewBox:"0 0 24 24",fill:"none",stroke:"currentColor",strokeWidth:2,strokeLinecap:"round",strokeLinejoin:"round"};/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const se=w.forwardRef(({color:n="currentColor",size:i=24,strokeWidth:p=2,absoluteStrokeWidth:y,className:v="",children:m,iconNode:S,...x},$)=>w.createElement("svg",{ref:$,...ie,width:i,height:i,stroke:n,strokeWidth:y?Number(p)*24/Number(i):p,className:K("lucide",v),...!m&&!ae(x)&&{"aria-hidden":"true"},...x},[...S.map(([C,R])=>w.createElement(C,R)),...Array.isArray(m)?m:[m]]));/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const h=(n,i)=>{const p=w.forwardRef(({className:y,...v},m)=>w.createElement(se,{ref:m,iconNode:i,className:K(`lucide-${oe(G(n))}`,`lucide-${n}`,y),...v}));return p.displayName=G(n),p};/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ce=[["path",{d:"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4",key:"ih7n3h"}],["polyline",{points:"7 10 12 15 17 10",key:"2ggqvy"}],["line",{x1:"12",x2:"12",y1:"15",y2:"3",key:"1vk2je"}]],Se=h("download",ce);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const le=[["path",{d:"m15 15 6 6",key:"1s409w"}],["path",{d:"m15 9 6-6",key:"ko1vev"}],["path",{d:"M21 16.2V21h-4.8",key:"1hrera"}],["path",{d:"M21 7.8V3h-4.8",key:"ul1q53"}],["path",{d:"M3 16.2V21h4.8",key:"1x04uo"}],["path",{d:"m3 21 6-6",key:"wwnumi"}],["path",{d:"M3 7.8V3h4.8",key:"1ijppm"}],["path",{d:"M9 9 3 3",key:"v551iv"}]],$e=h("expand",le);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const fe=[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["path",{d:"M12 16v-4",key:"1dtifu"}],["path",{d:"M12 8h.01",key:"e9boi3"}]],Ce=h("info",fe);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const pe=[["polyline",{points:"15 3 21 3 21 9",key:"mznyad"}],["polyline",{points:"9 21 3 21 3 15",key:"1avn1i"}],["line",{x1:"21",x2:"14",y1:"3",y2:"10",key:"ota7mn"}],["line",{x1:"3",x2:"10",y1:"21",y2:"14",key:"1atl0r"}]],Re=h("maximize-2",pe);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ye=[["path",{d:"M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z",key:"1lielz"}],["path",{d:"M12 7v6",key:"lw1j43"}],["path",{d:"M9 10h6",key:"9gxzsh"}]],Ee=h("message-square-plus",ye);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const de=[["line",{x1:"2",x2:"22",y1:"2",y2:"22",key:"a6p6uj"}],["path",{d:"M18.89 13.23A7.12 7.12 0 0 0 19 12v-2",key:"80xlxr"}],["path",{d:"M5 10v2a7 7 0 0 0 12 5",key:"p2k8kg"}],["path",{d:"M15 9.34V5a3 3 0 0 0-5.68-1.33",key:"1gzdoj"}],["path",{d:"M9 9v3a3 3 0 0 0 5.12 2.12",key:"r2i35w"}],["line",{x1:"12",x2:"12",y1:"19",y2:"22",key:"x3vr5v"}]],je=h("mic-off",de);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const he=[["path",{d:"M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z",key:"131961"}],["path",{d:"M19 10v2a7 7 0 0 1-14 0v-2",key:"1vc78b"}],["line",{x1:"12",x2:"12",y1:"19",y2:"22",key:"x3vr5v"}]],Oe=h("mic",he);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ke=[["polyline",{points:"4 14 10 14 10 20",key:"11kfnr"}],["polyline",{points:"20 10 14 10 14 4",key:"rlmsce"}],["line",{x1:"14",x2:"21",y1:"10",y2:"3",key:"o5lafz"}],["line",{x1:"3",x2:"10",y1:"21",y2:"14",key:"1atl0r"}]],Pe=h("minimize-2",ke);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ve=[["path",{d:"M3.714 3.048a.498.498 0 0 0-.683.627l2.843 7.627a2 2 0 0 1 0 1.396l-2.842 7.627a.498.498 0 0 0 .682.627l18-8.5a.5.5 0 0 0 0-.904z",key:"117uat"}],["path",{d:"M6 12h16",key:"s4cdu5"}]],Ne=h("send-horizontal",ve);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const me=[["path",{d:"M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z",key:"4pj2yx"}],["path",{d:"M20 3v4",key:"1olli1"}],["path",{d:"M22 5h-4",key:"1gvqau"}],["path",{d:"M4 17v2",key:"vumght"}],["path",{d:"M5 18H3",key:"zchphs"}]],Ae=h("sparkles",me);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const _e=[["path",{d:"M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4",key:"ih7n3h"}],["polyline",{points:"17 8 12 3 7 8",key:"t8dd8p"}],["line",{x1:"12",x2:"12",y1:"3",y2:"15",key:"widbto"}]],ze=h("upload",_e);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const we=[["path",{d:"m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72",key:"ul74o6"}],["path",{d:"m14 7 3 3",key:"1r5n42"}],["path",{d:"M5 6v4",key:"ilb8ba"}],["path",{d:"M19 14v4",key:"blhpug"}],["path",{d:"M10 2v2",key:"7u0qdc"}],["path",{d:"M7 8H3",key:"zfb6yr"}],["path",{d:"M21 16h-4",key:"1cnmox"}],["path",{d:"M11 3H9",key:"1obp7u"}]],qe=h("wand-sparkles",we);/**
 * @license lucide-react v0.503.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const xe=[["path",{d:"M18 6 6 18",key:"1bl5f8"}],["path",{d:"m6 6 12 12",key:"d8bk6v"}]],Le=h("x",xe);export{Se as D,$e as E,Ce as I,je as M,ge as R,Ae as S,ze as U,qe as W,Le as X,w as a,Me as b,be as c,Oe as d,Ne as e,Pe as f,te as g,Ee as h,Re as i,ne as r};
