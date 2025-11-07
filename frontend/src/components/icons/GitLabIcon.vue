<template>
  <img :src="gitlabLogo" :width="size" :height="size" alt="GitLab" class="gitlab-logo" />
</template>

<script setup>
import gitlabLogo from '../../assets/gitlab-logo.png'

defineProps({
  size: {
    type: [String, Number],
    default: 24
  }
})
</script>

<style scoped>
.gitlab-logo {
  display: block;
  object-fit: contain;
}
</style>
