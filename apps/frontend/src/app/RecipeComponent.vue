<script setup>
  import { shallowRef, onMounted } from 'vue';

  let recipes = shallowRef([])
  
  async function getData() {
    recipes.value = await (
      await fetch('http://127.0.0.1:8000/recipes/random')
      ).json()
    console.log(recipes.value)
  }

  onMounted(()=> {
    getData()
  })
</script>


<template>
  <div class="mt-4 flex gap-1 overflow-x-scroll max-w-full">
    <div 
      v-for="recipe in recipes"
      v-bind:key="recipe.recipe_id"
      class="duration-300 ease-in-out min-w-52 sm:w-64 h-72 flex
      flex-col items-center justify-center border-2 hover:border-4 hover:border-indigo-300 rounded-md"
    >
      <h2 class="font-bold text-center">{{ recipe.name }}</h2>
      <h3 class="italic">{{ recipe.category }}</h3>
      <h3>{{ recipe.cooking_time }} minutes</h3>
    </div>
  </div>
</template>
