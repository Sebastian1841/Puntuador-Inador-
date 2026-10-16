<script setup lang="ts">
import { useTheme } from '@/composables/useTheme';
import { useClub } from '@/composables/useClub';
const { theme, setTheme } = useTheme();
const { prefs, exportData } = useClub();
</script>

<template>
<fieldset class="theme-options"><legend>Apariencia</legend><button type="button" :aria-pressed="theme==='light'" @click="setTheme('light')">☀ Claro</button><button type="button" :aria-pressed="theme==='dark'" @click="setTheme('dark')">☾ Oscuro</button><small>Se guarda automáticamente en este navegador.</small></fieldset>
<label>Nombre del club<input v-model="prefs.name" required maxlength="60" />
</label>
<label class="color-field">Color de acento<input v-model="prefs.accent" type="color" />
</label>
<small class="accent-help">Vista previa inmediata. Pulsa «Guardar configuración» para conservar el color. El fondo, el logo y los colores de estado se mantienen.</small>
<div class="swatches">
<button v-for="c in ['#FF6600','#102372','#2D4450','#b5a2ff','#6cdddc']" :key="c" type="button" :style="{background:c}" :aria-pressed="prefs.accent.toLowerCase()===c.toLowerCase()" :aria-label="'Elegir color '+c" @click="prefs.accent=c" />
</div>
<label class="checkbox">
<input v-model="prefs.compact" type="checkbox" /> Colección compacta</label>
<button type="button" class="outline" @click="exportData">↓ Exportar datos del club (JSON)</button>
</template>
