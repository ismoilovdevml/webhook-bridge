<template>
  <svg viewBox="0 0 24 24" :width="size" :height="size" fill="currentColor">
    <circle cx="12" cy="12" r="10" fill="#0058CC"/>
    <circle cx="12" cy="12" r="5.8" fill="white"/>
    <path fill="#0058CC" d="M13.9 10.8c.7.3 1.3.9 1.6 1.6.3.7.4 1.5.2 2.3-.2.8-.6 1.4-1.2 1.9-.6.5-1.4.8-2.2.8h-1.5V9.5h1.5c.8 0 1.5.3 2.1.8.6.5 1 1.2 1.2 2 0 0 0 .1 0 .1-.2-.3-.5-.5-.9-.6-.4-.1-.8-.1-1.2.1-.4.2-.7.5-.9.9-.2.4-.2.8-.1 1.2.1.4.4.7.8.9.4.2.8.2 1.2.1.4-.1.7-.4.9-.8.2-.4.3-.8.2-1.2-.1-.4-.3-.8-.7-1z"/>
  </svg>
</template>

<script setup>
defineProps({
  size: {
    type: [String, Number],
    default: 24
  }
})
</script>
