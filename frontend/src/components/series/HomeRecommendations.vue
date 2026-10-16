<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import type { CatalogSeries } from '@/services/catalogApi'
import { apiRequest } from '@/services/http'
import { useClub } from '@/composables/useClub'
const props=withDefaults(defineProps<{expanded?:boolean}>(),{expanded:false})
const limit=ref(12)
const { data, save, busy, open, navigate } = useClub()
const results=ref<(CatalogSeries & {recommendation_reason?:string})[]>([]), loading=ref(true), failed=ref(false)
let controller: AbortController | undefined
const message=ref('')
const available=computed(()=>results.value.filter(item=>!data.series.some(s=>s.catalog_id===item.catalog_id&&(s.catalog_source||'tvmaze')===(item.catalog_source||'tvmaze'))))
const visible=computed(()=>available.value.slice(0,props.expanded?limit.value:4))
async function load() {
  controller?.abort()
  const current=new AbortController(); controller=current
  const timeout=setTimeout(()=>current.abort(),10000)
  loading.value=true; failed.value=false; message.value=''
  try {
    const items=await apiRequest<CatalogSeries[]>('catalog/recommendations',{signal:current.signal})
    if(controller===current)results.value=items
  } catch(error) {
    if(controller!==current)return
    failed.value=true
    message.value=current.signal.aborted?'La API local tardó demasiado en responder.':(error as Error).message
  } finally {
    clearTimeout(timeout)
    if(controller===current)loading.value=false
  }
}
watch(()=>data.active_profile_id,()=>{results.value=[];limit.value=12;load()})
async function add(item:CatalogSeries) { await save('series',{...item,catalog_source:item.catalog_source||'tvmaze',year:item.year??new Date().getFullYear(),status:'Pendiente',favorite:false,color:'#102372'}) }
onMounted(load)
onUnmounted(()=>{controller?.abort();controller=undefined})
</script>
<template>
<section class="home-recommendations" :class="{'recommendations-expanded':expanded}">
  <header class="shelf-heading"><h2>Recomendaciones para ti</h2><button v-if="!expanded" @click="navigate('Recomendaciones')">Ver más ›</button><button v-else :disabled="loading" @click="load">Actualizar</button></header>
  <p v-if="expanded" class="recommendations-intro">Sugerencias del catálogo guardado, ordenadas por los géneros de tus favoritas y series en seguimiento. Se excluyen los títulos de tu colección.</p>
  <div v-if="loading && !visible.length" class="recommendation-grid" aria-label="Cargando recomendaciones" aria-busy="true"><div v-for="n in 4" :key="n" class="recommendation-skeleton"></div></div>
  <div v-else-if="visible.length" class="recommendation-grid"><article v-for="item in visible" :key="item.catalog_id" class="recommendation-card"><img :src="item.image_url" alt="" loading="lazy" /><strong>{{item.title}}</strong><small v-if="expanded">{{item.recommendation_reason || item.genre}}</small><button :disabled="busy" @click="add(item)">+ Agregar a pendientes</button></article></div>
  <div v-else class="recommendation-empty"><p>{{failed?message:'Busca series en Explorar para descubrir sugerencias del catálogo.'}}</p><button class="outline" @click="failed?load():open('series')">{{failed?'Reintentar':'Explorar catálogo'}}</button></div>
<p v-if="failed && visible.length" role="status">Algunas sugerencias no se pudieron cargar. <button :disabled="loading" @click="load">Reintentar</button></p>
<button v-if="expanded && visible.length<available.length" class="outline recommendations-more" @click="limit+=12">Mostrar más recomendaciones</button>
</section>
</template>
