<script setup lang="ts">
defineProps<{ name: string }>()
const paths: Record<string,string> = {
 home:'M3 10 12 3l9 7M5 9v12h5v-7h4v7h5V9',
 book:'M12 5v16M12 5C8 2 5 3 2 4v15c4-1 7-1 10 2 3-3 6-3 10-2V4c-3-1-6-2-10 1Z',
 search:'M21 21l-5-5M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
 clock:'M12 7v5l4 2M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
 check:'m7 12 3 3 7-8M22 12a10 10 0 1 1-5-8',
 heart:'M20 4c-3-2-6-1-8 2-2-3-5-4-8-2-7 5 3 13 8 17 5-4 15-12 8-17Z',
 chart:'M3 21V9h4v12M10 21V3h4v18M17 21V6h4v15',
 users:'M16 21v-3c0-5-14-5-14 0v3M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M16 3c5 0 5 8 0 8M19 14c3 1 3 4 3 7',
 settings:'M9 3h6l1 3 3 1 2 5-2 5-3 1-1 3H9l-1-3-3-1-2-5 2-5 3-1 1-3ZM16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',
 play:'m6 3 15 9-15 9V3Z',
 calendar:'M3 5h18v16H3V5ZM3 10h18M7 2v6M17 2v6',
 activity:'M2 12h5l3-9 4 18 3-9h5',
 star:'m12 2 3 7 8 1-6 5 2 8-7-4-7 4 2-8-6-5 8-1 3-7Z',
 grid:'M3 3h7v7H3V3ZM14 3h7v7h-7V3ZM3 14h7v7H3v-7ZM14 14h7v7h-7v-7Z',
 list:'M9 5h13M9 12h13M9 19h13M2 5h1M2 12h1M2 19h1'
}
</script>
<template><svg class="ui-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="paths[name] || paths.star" /></svg></template>
