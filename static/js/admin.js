/*
====================================================
 Admin Dashboard Script (admin.js)
----------------------------------------------------
 Propósito general:
  - Unificar toda la lógica dinámica del panel de administración
  - Evitar inline scripts en la plantilla HTML para mejor mantenibilidad
  - Proveer inicializaciones modulares (tema, métricas, actividades, gráfico, token)

 Secciones principales:
  1. Mapeos globales de tipos de actividad (iconos + esquemas de color)
  2. Boot principal al DOMContentLoaded
     2.1. Toggle de tema (dark/light) con persistencia localStorage
     2.2. Actualización periódica de fecha y hora
     2.3. Carga de navbar dinámico (si existe loadNavbar)
     2.4. Lazy initialization del gráfico Chart.js mediante IntersectionObserver
     2.5. Construcción dinámica de métricas desde data-* attributes
     2.6. Sistema avanzado de actividades: paginación, filtro, auto-refresh, skeleton loaders, NEW badge
     2.7. Captura y limpieza de token en la URL (query param ?token=)

 Notas de diseño:
  - Se usa un patrón IIFE / funciones internas para aislar cada bloque lógico.
  - Dependencias blandas: loadNavbar(), checkInitialAuth() si están definidas en otros scripts.
  - Evitamos acoplar la plantilla a nombres de rutas backend: sólo usamos endpoints REST (/api/activities).
  - Las clases de color tailwind dinámicas (text-${m.color}-500) se construyen; asegurarse de que Tailwind JIT no sea necesario (usamos CDN base).

 Posibles mejoras futuras:
  - Sustituir números "hardcoded" (ej. total aplicaciones/rutas) por datos del backend.
  - Añadir manejo de errores visual (toasts / alertas accesibles) en lugar de un <li> rojo.
  - Internacionalización más robusta de fechas y mensajes.
====================================================
*/

// ---------------------------------------------------------------------------
// 1. Mapeos globales de tipos de actividad (iconos y colores)
// ---------------------------------------------------------------------------
window.__activityTypeMap = window.__activityTypeMap || {
  login:{ icon:'fa-sign-in-alt', color:'blue' },
  logout:{ icon:'fa-sign-out-alt', color:'gray' },
  create:{ icon:'fa-plus-circle', color:'green' },
  update:{ icon:'fa-edit', color:'indigo' },
  delete:{ icon:'fa-trash-alt', color:'red' },
  migration:{ icon:'fa-database', color:'purple' },
  error:{ icon:'fa-exclamation-triangle', color:'red' },
  user:{ icon:'fa-user-circle', color:'blue' },
  system:{ icon:'fa-cogs', color:'yellow' }
};
window.__activityColorBg = window.__activityColorBg || {
  blue:'bg-blue-100 text-blue-600',
  gray:'bg-gray-200 text-gray-600',
  green:'bg-green-100 text-green-600',
  indigo:'bg-indigo-100 text-indigo-600',
  red:'bg-red-100 text-red-600',
  purple:'bg-purple-100 text-purple-600',
  yellow:'bg-yellow-100 text-yellow-600'
};

// ---------------------------------------------------------------------------
// 2. Boot principal cuando el DOM está listo
// ---------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', ()=>{
  // 2.1 Toggle tema ---------------------------------------------------------
  (function themeToggle(){
    const btn = document.getElementById('theme-toggle');
    if(!btn) return; // tolerancia si el botón no está
    const sun = btn.querySelector('.sun');
    const moon = btn.querySelector('.moon');
    function currentTheme(){ return document.documentElement.classList.contains('light') ? 'light':'dark'; }
    function setTheme(t){
      // Reemplaza clase base 'light'/'dark'
      document.documentElement.className = document.documentElement.className.replace(/(light|dark)/g,'').trim();
      document.documentElement.classList.add(t);
      // Persistencia
      localStorage.setItem('admin-theme', t);
      // Estado accesible
      btn.setAttribute('aria-pressed', t==='dark');
      // Iconos
      if(sun && moon){
        if(t==='light'){ sun.style.opacity='1'; moon.style.opacity='0'; }
        else { sun.style.opacity='0'; moon.style.opacity='1'; }
      }
    }
    setTheme(currentTheme());
    btn.addEventListener('click', ()=>{
      document.body.classList.add('theme-switching');
      const next = currentTheme()==='dark' ? 'light':'dark';
      setTheme(next);
      setTimeout(()=>document.body.classList.remove('theme-switching'),450);
    });
  })();

  // 2.2 Fecha y hora --------------------------------------------------------
  function updateDateTime(){
    const now = new Date();
    const options = { weekday:'long', year:'numeric', month:'long', day:'numeric' };
    const d = document.getElementById('currentDate');
    const t = document.getElementById('currentTime');
    if(d) d.textContent = now.toLocaleDateString('es-ES', options);
    if(t) t.textContent = now.toLocaleTimeString('es-ES', { hour:'2-digit', minute:'2-digit'});
  }
  updateDateTime();
  setInterval(updateDateTime, 60000); // refresco minuto a minuto

  // 2.3 Verificación auth inicial (si existe) -------------------------------
  if(typeof window.checkInitialAuth === 'function'){
    window.checkInitialAuth();
  }

  // 2.4 Navbar dinámico -----------------------------------------------------
  if(typeof loadNavbar === 'function'){
    const container = document.getElementById('navbar-container');
    if(container) loadNavbar(container);
  }

  // 2.5 Gráfico (lazy load) -------------------------------------------------
  (function initActivityChartLazy(){
    const chartCanvas = document.getElementById('activityChart');
    if(!chartCanvas) return;
    const initChart = () => {
      if(chartCanvas._initialized) return; // evita reinicialización
      chartCanvas._initialized = true;
      const ctx = chartCanvas.getContext('2d');
      new Chart(ctx, {
        type:'line',
        data:{
          labels:['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'],
          datasets:[{
            label:'Actividad',
            data:[12,19,8,15,10,3,7], // Placeholder: reemplazar con datos reales si se desea
            backgroundColor:'rgba(99,102,241,0.2)',
            borderColor:'rgba(99,102,241,1)',
            borderWidth:2,
            tension:0.4,
            pointBackgroundColor:'rgba(99,102,241,1)',
            pointRadius:4
          }]
        },
        options:{
          responsive:true,
            maintainAspectRatio:false,
            scales:{
              y:{ beginAtZero:true, grid:{ color:'rgba(0,0,0,0.05)'} },
              x:{ grid:{ display:false } }
            },
            plugins:{
              legend:{ display:false },
              tooltip:{
                backgroundColor:'rgba(255,255,255,0.9)',
                titleColor:'#1f2937',
                bodyColor:'#4b5563',
                borderColor:'rgba(203,213,225,1)',
                borderWidth:1,
                padding:10,
                displayColors:false
              }
            }
        }
      });
    };
    const io = new IntersectionObserver(entries=>{
      entries.forEach(e=>{ if(e.isIntersecting){ initChart(); io.disconnect(); } });
    });
    io.observe(chartCanvas);
  })();

  // 2.6 Métricas dinámicas --------------------------------------------------
  (function buildMetrics(){
    const grid = document.getElementById('metrics-grid');
    if(!grid) return;
    const userCount = parseInt(grid.getAttribute('data-user-count')) || 0;
    const activityCount = parseInt(grid.getAttribute('data-activity-count')) || 0;
    const metricsData = [
      { label:'Total Usuarios', value: userCount, icon:'fa-users', color:'blue', link:'/usuarios_admin/' },
      { label:'Migraciones', value: activityCount, icon:'fa-database', color:'purple', link:'/migraciones/admin_migraciones' },
      { label:'Aplicaciones', value: 4, icon:'fa-laptop-code', color:'green', link:'#' },  // TODO: reemplazar con valor real
      { label:'Rutas', value: 4, icon:'fa-route', color:'indigo', link:'#' }              // TODO: reemplazar con valor real
    ];
    const colorMap = { blue:'bg-blue-500', purple:'bg-purple-500', green:'bg-green-500', indigo:'bg-indigo-500' };
    grid.innerHTML = metricsData.map((m,i)=>`<div class="panel-surface rounded-xl shadow-md overflow-hidden card-hover focus-within:ring-2 focus-within:ring-${m.color}-500 transition">
  <div class="p-5">
    <div class="flex items-center">
      <div class="flex-shrink-0 ${colorMap[m.color]||'bg-gray-500'} rounded-full p-3" aria-hidden="true">
        <i class="fas ${m.icon} text-white text-xl"></i>
      </div>
      <div class="ml-5">
        <p class="text-sm font-medium text-soft truncate">${m.label}</p>
        <p class="mt-1 text-3xl font-semibold">${m.value}</p>
      </div>
    </div>
  </div>
  <div class="panel-alt px-5 py-3 text-sm">
    <a href="${m.link}" class="font-medium text-${m.color}-500 hover:text-${m.color}-600 inline-flex items-center gap-2 group" aria-label="Ver detalles ${m.label}">
      Ver detalles <i class="fas fa-arrow-right text-xs group-hover:translate-x-0.5 transform transition"></i>
    </a>
  </div>
</div>`).join('');
    // Animación escalonada
    [...grid.children].forEach((el,idx)=>{
      el.classList.add('fade-in-up');
      el.style.animationDelay = (idx*90)+'ms';
    });
  })();

  // 2.7 Sistema avanzado de actividades ------------------------------------
  const skeletonHTML = (count=5)=>'<li class="animate-pulse flex items-start gap-3" role="presentation">'
    +'<div class="h-8 w-8 rounded-full bg-gray-200"></div>'
    +'<div class="flex-1 space-y-2"><div class="h-3 bg-gray-200 rounded w-2/3"></div><div class="h-3 bg-gray-200 rounded w-1/3"></div></div>'
    +'</li>'.repeat(count);

  (function activitySystem(){
    const btn = document.getElementById('refresh-activities');
    const chk = document.getElementById('auto-refresh-activities');
    const list = document.getElementById('activity-list');
    const loadMoreBtn = document.getElementById('load-more-activities');
    const filterSelect = document.getElementById('activity-type-filter');
    const scrollContainer = document.getElementById('activity-scroll-container');
    if(!btn || !list || !chk || !loadMoreBtn || !filterSelect || !scrollContainer) return; // tolerancia

    // Spinner inline
    const spinner = document.createElement('span');
    spinner.className='ml-2 hidden animate-spin text-xs';
    spinner.innerHTML='<i class="fas fa-spinner"></i>';
    btn.appendChild(spinner);

    // Persistencia auto-refresh
    const LS_KEY = 'admin-auto-refresh-activities';
    const saved = localStorage.getItem(LS_KEY)==='true';
    chk.checked = saved;

    // Utilidades internas
    let intervalId = null;
    const rtf = (typeof Intl!=='undefined' && Intl.RelativeTimeFormat)
      ? new Intl.RelativeTimeFormat('es', { numeric:'auto' })
      : null;

    function formatRelative(date){
      if(!date) return '';
      const diffSec = Math.round((date.getTime()-Date.now())/1000); // positivo si futuro
      const ranges = [
        {unit:'day',secs:86400},
        {unit:'hour',secs:3600},
        {unit:'minute',secs:60},
        {unit:'second',secs:1}
      ];
      if(rtf){
        for(const r of ranges){
          if(Math.abs(diffSec) >= r.secs || r.unit==='second')
            return rtf.format(Math.round(diffSec/r.secs), r.unit);
        }
      }
      // Fallback manual
      const diff = -diffSec; // convertir a tiempo transcurrido positivo
      if(diff < 60) return 'hace segundos';
      if(diff < 3600) return 'hace '+Math.floor(diff/60)+' min';
      if(diff < 86400) return 'hace '+Math.floor(diff/3600)+' h';
      return date.toLocaleDateString('es-ES');
    }

    // Estado de paginación
    let page = 0;
    const pageSize = 10;
    let loading=false;
    let hasMore=true;
    let currentFilter='';

    function clearList(){
      list.innerHTML='';
      page=0;
      hasMore=true;
      list.dataset.hasMore='true';
      loadMoreBtn.disabled=false;
    }
    function preserveScroll(run){
      const prev=scrollContainer.scrollTop;
      run();
      scrollContainer.scrollTop=prev;
    }
    function buildQuery(){
      const p=new URLSearchParams();
      p.set('limit',pageSize);
      p.set('offset',page*pageSize);
      if(currentFilter) p.set('type',currentFilter);
      return '/api/activities?'+p.toString();
    }
    function activityVisual(a){
      const m=window.__activityTypeMap||{};
      const t=(a.type||'').toLowerCase();
      return m[t] || { icon:'fa-user-circle', color:'blue' };
    }
    const colorBg = window.__activityColorBg || {};

    async function fetchActivities({append=false, showSkeleton=false}={}){
      if(loading) return;
      loading=true;
      if(showSkeleton && !append){ list.innerHTML = skeletonHTML(5); }
      spinner.classList.remove('hidden');
      btn.disabled=true; btn.classList.add('opacity-60','cursor-not-allowed');
      try {
        const res = await fetch(buildQuery());
        if(!res.ok) throw new Error('HTTP '+res.status);
        const data = await res.json();
        if(!Array.isArray(data) || !data.length){
          if(!append){ list.innerHTML='<li class="text-sm text-soft">Sin actividades</li>'; }
          hasMore=false; loadMoreBtn.disabled=true; return;
        }
        if(data.length < pageSize){ hasMore=false; loadMoreBtn.disabled=true; }
        const now = Date.now();
        const newMarkup = data.map((a,i)=>{
          const when=a.timestamp?new Date(a.timestamp):null;
          const rel=formatRelative(when);
          const vis=activityVisual(a);
          const vColor=colorBg[vis.color]||colorBg.blue||'bg-blue-100 text-blue-600';
          const isNew= when && (now-when.getTime())<5*60*1000; // <5 minutos
          const badge=isNew?'<span class="ml-2 inline-block px-2 py-0.5 text-[10px] rounded bg-green-100 text-green-700 font-medium tracking-wide">NUEVO</span>':'';
          return `<li class=\"pb-3 border-b border-gray-100 last:border-0 flex items-start fade-in-up\" style=\"animation-delay:${(page*pageSize+i)*25}ms\" role=\"listitem\">\n`
            + `    <div class=\"h-8 w-8 rounded-full ${vColor} flex items-center justify-center mr-3 mt-0.5\" aria-hidden=\"true\"><i class=\"fas ${vis.icon}\"></i></div>\n`
            + `    <div class=\"flex-1\">\n`
            + `    <p class=\"text-sm flex items-center flex-wrap\"><span class=\"font-medium\">${a.user||'Usuario'}<\/span> <span class=\"mx-1\">${a.action||''}<\/span>${badge}</p>\n`
            + `    <p class=\"text-xs text-soft mt-1\"><time datetime=\"${a.timestamp||''}\">${rel}<\/time></p>\n`
            + `    </div>\n`
            + `    </li>`;
        }).join('');
        if(append){ preserveScroll(()=>list.insertAdjacentHTML('beforeend', newMarkup)); }
        else { list.innerHTML=newMarkup; }
        page++;
      } catch(err){
        console.error(err);
        list.insertAdjacentHTML('afterbegin','<li class="text-xs text-red-500">Error al cargar actividades</li>');
      } finally {
        spinner.classList.add('hidden');
        btn.disabled=false; btn.classList.remove('opacity-60','cursor-not-allowed');
        loading=false; loadMoreBtn.disabled=!hasMore;
      }
    }

    function startInterval(){ if(intervalId) return; intervalId=setInterval(()=>fetchActivities({append:false}),60000); }
    function clearIntervalRefresh(){ if(intervalId){ clearInterval(intervalId); intervalId=null; } }

    // Eventos UI
    chk.addEventListener('change', ()=>{
      const enabled=chk.checked;
      localStorage.setItem(LS_KEY, enabled);
      if(enabled){
        startInterval();
        fetchActivities({append:false});
      } else { clearIntervalRefresh(); }
    });
    btn.addEventListener('click', ()=>fetchActivities({append:false, showSkeleton:true}));
    if(loadMoreBtn) loadMoreBtn.addEventListener('click', ()=>{ if(hasMore) fetchActivities({append:true}); });
    if(filterSelect) filterSelect.addEventListener('change', (e)=>{ currentFilter=e.target.value; clearList(); fetchActivities({append:false, showSkeleton:true}); });

    // Primera carga
    fetchActivities({append:false, showSkeleton:true});
    if(saved) startInterval();
  })();

  // 2.8 Captura de token en URL ---------------------------------------------
  (function tokenCapture(){
    try {
      const urlParams = new URLSearchParams(window.location.search);
      const token = urlParams.get('token');
      if(token){
        localStorage.setItem('access_token', token);
        urlParams.delete('token');
        const cleanUrl = window.location.pathname + (urlParams.toString()? '?' + urlParams.toString(): '');
        window.history.replaceState({}, document.title, cleanUrl);
      }
    } catch(e){ console.warn('Token capture error', e); }
  })();
});
