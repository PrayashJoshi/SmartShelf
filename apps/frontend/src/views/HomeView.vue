<script setup lang="ts">
import Home from '../app/Home.vue'
</script>

<template>
  <main class="main">
    <Home/>
  </main>
</template>

<style>
@media (min-width: 768px) {
  .main {
    max-width: 768px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 1rem;
    height: 1dvh
  }
}
</style>
