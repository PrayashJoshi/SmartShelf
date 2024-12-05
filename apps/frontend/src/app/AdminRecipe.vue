<script lang="ts" setup>
  import { onMounted, ref } from 'vue';

  let name = ref('')
  let category = ref('')
  let origin = ref('')
  let cooktime = ref(0)
  let difficulty = ref('Easy')

  let ingName = ref('')
  let ingQuantity = ref('')
  let ingUnit = ref('')

  const addNew = ref(false)
  const error = ref(false)

  type Ingredient = {
    name: string;
    quantity?: number;
    measurement_unit: string;
  }

  const ingredients = ref<Ingredient[]>([]);

  function addTodo() {
    if (ingName.value.trim() === "") {
      return;
    }

    ingredients.value.unshift({
      name: ingName.value,
      quantity: Number.parseFloat(ingQuantity.value),
      measurement_unit: ingUnit.value
    });

    ingName.value = "";
    ingQuantity.value = "";
    ingUnit.value = "";
    console.log(ingredients.value)
  }

  function deleteTodo(ingredient: Ingredient) {
    ingredients.value = ingredients.value.filter((x) => x !== ingredient);
  }

  function submitRecipe() {
    if (ingredients.value.length === 0) {
      error.value = true
      return
    }
  }

</script>

<template>
  <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
    Add Recipe
  </h2>

  <form id="main-form" @submit.prevent="submitRecipe"/>
  <form id="ingredient-form" @submit.prevent="addTodo"/>

  <section id="recipe-questions">
    <div>
      <label for="name" class="mt-2 block text-sm font-medium leading-6
        text-gray-900">Name</label>
      <input id="name" name="text" v-model="name" type="text" form="main-form" required
      class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
      shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
      focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
    </div>
    <div>
      <label for="category" class="mt-2 block text-sm font-medium leading-6
        text-gray-900">Category (eg. Main Dish, Side, Dessert)</label>
      <input id="category" name="text" v-model="category" type="text" form="main-form" required
      class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
      shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
      focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
    </div>
    <div>
      <label for="name" class="mt-2 block text-sm font-medium leading-6
        text-gray-900">Cuisine Origin (eg. American, Japanese, Middle Eastern)</label>
      <input id="name" name="text" v-model="origin" type="text" form="main-form" required
      class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
      shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
      focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
    </div>
    <div>
      <label for="cooktime" class="mt-2 block text-sm font-medium leading-6
        text-gray-900">Estimated Cooking Time (minutes)</label>
      <input id="cooktime" name="cooktime" v-model="cooktime" type="number" form="main-form" required
      class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
      shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
      focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
    </div>
    <div>
      <label for="difficulty" class="mt-2 block text-sm font-medium leading-6
        text-gray-900">Difficulty</label>
      <select id="difficulty" v-model="difficulty"
        class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
        shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
        focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
        <option disabled value="">Please select one</option>
        <option value="Easy">Easy</option>
        <option value="Medium">Medium</option>
        <option value="Hard">Hard</option>
      </select>
    </div>
  </section>

  <div>
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate
        sm:text-xl mt-3 sm:tracking-tight">
        Ingredients
      </h2>
      <button @click="addNew = !addNew">
        {{ addNew ? 'Hide' : 'Add New Ingredient' }}
      </button>
    </div>
    <section id="ingredient-questions" v-if="addNew">
      <div class="grid grid-cols-3">
        <div>
          <label for="ingredient-name" class="mt-2 block text-sm font-medium leading-6
            text-gray-900">Name</label>
          <input id="ingredient-name" v-model="ingName" form="ingredient-form" name="cooktime" type="text" required
          class="block rounded-md border-0 px-1.5 py-1.5 text-gray-900
          shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
          focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
        </div>
        <div>
          <label for="quantity" class="mt-2 block text-sm font-medium leading-6
            text-gray-900">Quantity</label>
          <input id="quantity" name="quantity" v-model="ingQuantity" form="ingredient-form" type="number" required
          class="block rounded-md border-0 px-1.5 py-1.5 text-gray-900
          shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
          focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
        </div>
        <div>
          <label for="unit" form="ingredient-form" class="mt-2 block text-sm font-medium leading-6
            text-gray-900">Measurement Unit</label>
          <input id="unit" name="unit" v-model="ingUnit" type="text" required
          class="block rounded-md border-0 px-1.5 py-1.5 text-gray-900
          shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
          focus:ring-2 focus:ring-inset sm:text-sm sm:leading-6">
        </div>
      </div>
      <button type="submit" form="ingredient-form"
        class="flex justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
        hover:bg-red-500 focus-visible:outline focus-visible:outline-2 mt-2
        focus-visible:outline-offset-2 focus-visible:outline-red-600">
        Add Ingredient
      </button>
    </section>


    <ul class='mt-5 max-h-64'>
      <li
        id="ingredient-information"
        v-for="ingredient in ingredients"
        v-bind:key="ingredient.name"
        class="flex p-2 mt-2 w-100 border-2 border-gray-300 rounded justify-between
        items-center"
        >
        <div>
          <input type="text" v-model="ingredient.name" />
          <input type="text" class="w-4" v-model="ingredient.quantity" />
          <input type="text" class="w-12" v-model="ingredient.measurement_unit" />
        </div>
        <button type="button" @click="deleteTodo(ingredient)" class="text-gray-400
          bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex 
          justify-center items-center " data-modal-hide="default-modal">
          <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
          </svg>
          <span class="sr-only">Close modal</span>
        </button>
      </li>
    </ul>
  </div>

  <button
      form="main-form"
      class="flex mb-5 w-full justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
      hover:bg-red-500 focus-visible:outline focus-visible:outline-2 mt-2
      focus-visible:outline-offset-2 focus-visible:outline-red-600">
      Add New Recipe
  </button>
  <p class="text-center text-red-500" v-if="error">Cannot Add Recipe, No Ingredients</p>

</template>
