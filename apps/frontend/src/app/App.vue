<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import { store } from '../store.ts'
</script>

<template>
  <header>
    <nav v-if="store.loggedIn">
      <!-- TODO: adjust to make user custom link -->
      <RouterLink to="/about">About</RouterLink>
      <RouterLink to="/login">Logout</RouterLink>
    </nav>
  </header>
  <RouterView />
</template>

<style scoped lang="css">
header {
  line-height: 1.5;
  max-width: 100vw;
}

nav>a {
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 768px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
    margin-left: auto;
    margin-right: auto;
    max-width: 768px;
  }

  nav {
    text-align: left;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
}
</style>
