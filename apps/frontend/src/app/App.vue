<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import { store } from '../store.ts'
</script>

<template>
  <header>
    <nav class="invisible lg:visible" v-if="store.loggedIn">
      <!-- TODO: adjust to make user custom link -->
      <RouterLink to="/">About</RouterLink>
      <RouterLink to="/login">Logout</RouterLink>
    </nav>
  </header>
  <RouterView />
    <nav class="visible absolute inset-x-0 bottom-0 h-12 bg-indigo-600 lg:invisible" v-if="store.loggedIn">
      <div class="absolute left-0 right-0 bottom-5 ms-auto me-auto w-fit">
        <button class="bg-indigo-400 w-10 h-10 text-white rounded-full">+</button>
      </div>
      <div class="flex items-center justify-between h-full mx-2 text-white">
        <!-- TODO: adjust to make user custom link -->
        <RouterLink to="/">About</RouterLink>
        <RouterLink to="/login">Logout</RouterLink>
      </div>
    </nav>
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
