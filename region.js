(function(){
  var ALIAS={gb:"uk"};
  function region(){
    var langs=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||""]);
    for(var i=0;i<langs.length;i++){
      var m=/[-_]([A-Za-z]{2})$/.exec(langs[i]||"");
      if(m){var r=m[1].toLowerCase();return ALIAS[r]||r;}
    }
    return "ph";
  }
  var R=region();
  if(R==="ph")return;
  function fix(root){
    var as=(root.querySelectorAll?root:document).querySelectorAll('a[href*="justwatch.com/ph"]');
    for(var i=0;i<as.length;i++){as[i].href=as[i].href.replace("justwatch.com/ph","justwatch.com/"+R);}
  }
  function run(){
    fix(document);
    new MutationObserver(function(ms){for(var i=0;i<ms.length;i++){for(var j=0;j<ms[i].addedNodes.length;j++){var n=ms[i].addedNodes[j];if(n.nodeType===1)fix(n.parentNode||n);}}}).observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",run);else run();
})();
