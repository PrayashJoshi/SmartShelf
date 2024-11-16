<script lang="ts" setup>
  import { ref, onMounted, watch } from "vue";

  type Ingredient = {
    name: string,
    price: string
  }

  const ingredients = ref<Ingredient[]>([]);
  const text = ref("");
  const price = ref("");
  function addTodo() {
    if (text.value.trim() === "") {
      return;
    }

    ingredients.value.unshift({
      name: text.value,
      price: price.value
    });

    text.value = "";
    price.value = "";
    console.log(ingredients.value)
  }

  function deleteTodo(ingredient: Ingredient) {
    ingredients.value = ingredients.value.filter((x) => x !== ingredient);
  }

  async function upload() {
    const res = await fetch('http://localhost:8000/users/add_user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
      }),
    })
  }

</script>

<template>
  <div class="m-2 lg:m-0 lg:flex lg:flex-col lg:items-start lg:justify-between">
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
        Upload Your Receipt
      </h2>
    </div>

    <!-- <div class="mt-4">
      <label for="photo" class="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-sm"> Upload Photo</label>
      <input id="photo" class="hidden" type="file"/>
    </div> -->


    <div class="mt-4">
      <h3>Manually Input Ingredients</h3>
      <form @submit.prevent="addTodo">
        <input required class="m-2" type="text" placeholder="e.g. Eggs" v-model="text"/>
        <input required class="m-2" type="text" placeholder="Price" v-model="price"/>
        <input type="submit" value="Add Ingredient" />
      </form>
    </div>

    <h2 class="text-xl font-bold leading-7 mt-8 mb-2 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
      Your Receipt
    </h2>

    <div class="h-64 w-full overflow-auto overflow-x-hidden scroll-m-0">
      <div class="grid grid-cols-1 gap-2 content-between ">
        <div
          v-for="ingredient in ingredients"
          v-bind:key="ingredient.name"
          class="flex p-2 w-100 border-2 border-gray-300 rounded justify-between"
        >
          <div>
            <input type="text" v-model="ingredient.name" />
            <input type="text" class="w-12" v-model="ingredient.price" />
          </div>

          <div >
            <button class="text-red-400" @click="deleteTodo(ingredient)">Delete</button>
          </div>
        </div>
      </div>
    </div>
    
      <button class="w-full lg:inline mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white" @onclick="upload">
          Upload Receipt
      </button>

  </div>
</template>