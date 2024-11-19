<script setup lang="ts">
import Receipt from '../app/Receipt.vue'
</script>

<template>
  <main class="main">
    <Receipt/>
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
