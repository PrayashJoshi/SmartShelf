<script setup lang="ts">
import Admin from '../app/Admin.vue'
</script>

<template>
  <main class="main">
    <Admin/>
  </main>
</template>

<style>
@media (min-width: 768px) {
  .main {
    max-width: 768px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 1rem;
  }
}
</style>
