<script setup lang="ts">
import Test from '../app/Test.vue'
</script>

<template>
  <main class="about">
    <Test/>
  </main>
</template>

<style>
@media (min-width: 768px) {
  .about {
    max-width: 768px;
    margin-left: auto;
    margin-right: auto;
    padding: 0 1rem;
  }
}
</style>
