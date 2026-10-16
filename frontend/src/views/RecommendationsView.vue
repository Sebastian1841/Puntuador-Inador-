<script setup lang="ts">
import HomeRecommendations from '@/components/series/HomeRecommendations.vue'
import { useClub } from '@/composables/useClub'
const { navigate }=useClub()
</script>
<template><div class="recommendations-page"><button class="outline" @click="navigate('Biblioteca')">← Volver a Inicio</button><HomeRecommendations expanded /></div></template>
