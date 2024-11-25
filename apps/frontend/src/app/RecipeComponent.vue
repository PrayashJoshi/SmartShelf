<script setup>
  import { shallowRef, onMounted, ref } from 'vue';

  const recipes = shallowRef([])
  const ingredients = shallowRef([])
  const modalRecipe = shallowRef()
  const displayModal = ref(false)
  const imgSrc = ref('')
  
  async function getData() {
    recipes.value = await (
      await fetch('http://127.0.0.1:8000/recipes/random')
      ).json()
    console.log(recipes.value)
  }

  async function display (recipe) {
    modalRecipe.value = recipe
    console.log(modalRecipe.value)
    const ingredientData = await (
      await fetch(`http://127.0.0.1:8000/ingredients/${recipe.recipe_id}`)
    ).json()

    const imgData = await (
      await fetch(`https://api.dub.co/metatags?url=https://www.food.com/recipe/${recipe.url}`)
    ).json()

    console.log(ingredientData)
    console.log(imgData)
    ingredients.value = ingredientData
    if (imgData.image ===
        "https://geniuskitchen.sndimg.com/fdc-new/img/fdc-shareGraphic.png"){
      imgSrc.value = ''
    }
    else{
      imgSrc.value = imgData.image
    }

    toggle()
  }

  function toggle() {
    displayModal.value = !displayModal.value  
  }

  onMounted(async ()=> {
    await getData()
  })
</script>


<template>

  <div class="mt-4 flex gap-1 overflow-x-scroll max-w-full">
    <div 
      v-for="recipe in recipes"
      :key="recipe.recipe_id"
      
      @click="display(recipe)"
      class="duration-300 ease-in-out min-w-52 sm:w-64 h-72 flex
      flex-col items-center justify-center border-2 hover:border-4 hover:border-indigo-300 rounded-md"
    >
      <h2 class="font-bold text-center">{{ recipe.name }}</h2>
      <h3 class="italic">{{ recipe.category }}</h3>
      <h3>{{ recipe.cooking_time }} minutes</h3>
    </div>
  </div>

  <div id="default-modal" tab="-1" v-show="displayModal" class="overflow-y-auto
      overflow-x-hidden fixed top-0 right-0 left-0 z-50 grid 
      place-items-center w-full md:inset-0 h-[calc(100%-1rem)] max-h-full bg-black/25">
    <div class="relative p-4 w-full max-w-2xl max-h-full col-span-2">
        <!-- Modal content -->
        <div class="relative bg-white rounded-lg shadow">
            <!-- Modal header -->
            <div class="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600">
                <h3 class="text-xl font-semibold text-white-900 ">
                    Ingredients for {{ modalRecipe?.name }}
                </h3>
                <button type="button" @click="toggle" class="text-gray-400
                    bg-transparent hover:bg-blue-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex 
                    justify-center items-center " data-modal-hide="default-modal">
                    <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                    </svg>
                    <span class="sr-only">Close modal</span>
                </button>
            </div>
            <!-- Modal body -->
            <div class="p-4 md:p-5 space-y-4">
                <img class="align-center max-w-64" :src="imgSrc"/>
                <a class="text-sky-500 underline" target="_blank" rel="noopener noreferrer" :href="'https://www.food.com/recipe/'+modalRecipe?.url"> Actual Recipe Here </a>
                <ul v-for="(ingredient, i) in ingredients"
                    :key="ingredient.name+i">
                  <li class="grid grid-cols-3">
                      <span>{{ingredient.name}}</span>
                  </li>
                </ul>
                <button class="w-full lg:inline mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white">
                    Generate Shopping List
                </button>

            </div>
        </div>
    </div>
  </div>

</template>
