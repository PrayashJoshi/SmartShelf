<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router';
import { store } from '../store'

function logout(){
  store.loggedIn = false
}

</script>

<template>
  <header>
    <nav class="invisible lg:visible" v-if="store.loggedIn">
      <!-- TODO: adjust to make user custom link -->
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/profile">Profile</RouterLink>
      <RouterLink v-if="store.user.admin" to="/admin/dash">Dashboard</RouterLink>
      <RouterLink to="/login" @click="logout">Logout</RouterLink>
    </nav>
  </header>
  <RouterView />
  <nav class="visible fixed inset-x-0 bottom-0 h-12 bg-indigo-600 lg:invisible" v-if="store.loggedIn">
    <div class="flex items-center justify-between h-full mx-2 text-white">
      <!-- TODO: adjust to make user custom link -->
      <RouterLink to="/">Home</RouterLink>
      <RouterLink to="/profile">Profile</RouterLink>
      <RouterLink v-if="store.user.admin" to="/admin/dash">Dashboard</RouterLink>
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
