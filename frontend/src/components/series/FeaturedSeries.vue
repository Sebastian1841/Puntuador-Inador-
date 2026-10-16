<script setup lang="ts">
import { useClub } from '@/composables/useClub';
const { average, votes, top, open } = useClub();
</script>

<template>
<section class="hero">
<div class="hero-copy">
<div class="pill">✦ {{top?'MEJOR PROMEDIO POR CAPÍTULO':'TU PRÓXIMA GRAN HISTORIA'}}</div>
<h2>{{top?.title || 'Una serie termina.\nLa conversación sigue.'}}</h2>
<p>{{top?.description || 'Ese final que nadie esperaba. Ese personaje que todos aman. Un lugar para las series que no dejamos de comentar.'}}</p>
<div class="hero-bottom">
<button @click="top?open('detail',top):open('series')">{{top?'Ver capítulos':'Empezar la colección'}} <span>↗</span>
</button>
<span v-if="top" class="hero-score">★ {{average(top.id).toFixed(1)}} <small>/ 5 · {{votes(top.id)}} capítulos puntuados</small>
</span>
<span v-else class="hero-score">½ <small>estrella a la vez, capítulo a capítulo</small>
</span>
</div>
</div>
<div class="hero-art" aria-hidden="true">
<div class="orbit orbit-one">
</div>
<div class="orbit orbit-two">
</div>
<div class="big-star">✦</div>
<span class="art-caption">ONE MORE<br>EPISODE.</span>
<span class="art-index">EST. 2026 / YOUR SERIES CLUB</span>
</div>
</section>
</template>
