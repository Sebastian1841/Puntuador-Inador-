<script setup lang="ts">
import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
import UiIcon from '../components/layout/UiIcon.vue'
import SeriesCard from '../components/series/SeriesCard.vue'
import { useClub } from '../composables/useClub'
const favorites=ref(false)
const { data, loading, average, open } = useClub()
const search=ref(''), filter=ref('Todas'), genre=ref('Todas'), order=ref('recent'), layout=ref('grid'), limit=ref(24)
const scoped=computed(()=>data.series)
const genres=computed(()=>[...new Set(scoped.value.flatMap(s=>s.genre.split(',').map(g=>g.trim()).filter(Boolean)))].sort())
const normalize=(s:string)=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()
const visible=computed(()=>scoped.value.filter(s=>(filter.value==='Todas'||s.status===filter.value)&&(!favorites.value||s.favorite)&&(genre.value==='Todas'||s.genre.split(',').some(g=>normalize(g.trim())===normalize(genre.value)))&&normalize(`${s.title} ${s.original_title||''}`).includes(normalize(search.value.trim()))))
const displayed=computed(()=>{const list=[...visible.value]; if(order.value==='title')list.sort((a,b)=>a.title.localeCompare(b.title,'es')); if(order.value==='score')list.sort((a,b)=>average(b.id)-average(a.id)); return list.slice(0,limit.value)})
const active=computed(()=>!!search.value||filter.value!=='Todas'||genre.value!=='Todas'||favorites.value||order.value!=='recent')
function clear(){search.value='';filter.value='Todas';genre.value='Todas';favorites.value=false;order.value='recent'}
const states:Record<string,string>={siguiendo:'Viendo',pendiente:'Pendiente',terminada:'Terminada'}
function readUrl(){const q=new URLSearchParams(location.hash.split('?')[1]||'');filter.value=states[q.get('estado')||'']||'Todas';genre.value=q.get('genero')||'Todas';favorites.value=q.get('favoritas')==='true';search.value=q.get('q')||'';order.value=['title','score'].includes(q.get('orden')||'')?q.get('orden')!:'recent'}
readUrl()
watch([search,filter,genre,favorites,order],()=>{limit.value=24;const q=new URLSearchParams();const state=Object.keys(states).find(k=>states[k]===filter.value);if(state)q.set('estado',state);if(genre.value!=='Todas')q.set('genero',genre.value);if(favorites.value)q.set('favoritas','true');if(search.value)q.set('q',search.value);if(order.value!=='recent')q.set('orden',order.value);const query=q.toString();history.replaceState(null,'',`#/coleccion${query?'?'+query:''}`)})
watch(()=>data.active_profile_id,clear)
onMounted(()=>window.addEventListener('hashchange',readUrl))
onUnmounted(()=>window.removeEventListener('hashchange',readUrl))
</script>
<template><div class="dashboard-home collection-module library-module">
<div class="library-heading"><span class="library-icon"><UiIcon name="book" /></span><div><h1>Mi colección</h1><p>Todas las series que sigues, has visto o quieres ver. Lleva tu progreso al día.</p></div></div>
<div class="library-search-row"><label><UiIcon name="search" /><input v-model="search" placeholder="Buscar en mi colección..." aria-label="Buscar en mi colección" /></label><button class="primary" @click="open('series')">＋ Agregar serie</button></div>
<div class="library-filterbar"><label>Estado<select v-model="filter"><option value="Todas">Todos</option><option value="Viendo">Siguiendo</option><option value="Pendiente">Pendientes</option><option value="Terminada">Terminadas</option></select></label><label>Género<select v-model="genre"><option value="Todas">Todos</option><option v-for="g in genres" :key="g">{{g}}</option></select></label><label>Ordenar por<select v-model="order"><option value="recent">Agregadas recientemente</option><option value="title">Nombre</option><option value="score">Puntuación</option></select></label><label class="library-favorites"><input v-model="favorites" type="checkbox" role="switch" />Solo favoritas</label><button v-if="active" class="outline" @click="clear">Limpiar filtros</button><div class="layout-toggle"><button :class="{active:layout==='grid'}" :aria-pressed="layout==='grid'" aria-label="Vista de tarjetas" @click="layout='grid'"><UiIcon name="grid" /></button><button :class="{active:layout==='list'}" :aria-pressed="layout==='list'" aria-label="Vista de lista" @click="layout='list'"><UiIcon name="list" /></button></div></div>
<p class="library-count" role="status">{{visible.length}} series</p>
<p v-if="loading" class="empty">Cargando tu colección…</p><div v-else-if="!displayed.length" class="empty"><h2>{{data.series.length?'No hay coincidencias':'Tu colección empieza aquí'}}</h2><button class="outline" @click="data.series.length?clear():open('series')">{{data.series.length?'Limpiar filtros':'Agregar serie'}}</button></div>
<div v-else class="collection-grid" :class="{'collection-list':layout==='list',compact:data.settings.compact}"><SeriesCard v-for="s in displayed" :key="s.id" :s="s" /></div><div v-if="displayed.length<visible.length" class="load-more"><button class="outline" @click="limit+=24">Mostrar más series</button></div>
</div></template>
