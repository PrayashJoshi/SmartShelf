<script setup lang="ts">

import Upload from '../app/Upload.vue';

</script>

<template>
  <div class="main">
    <Upload/>
  </div>
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
