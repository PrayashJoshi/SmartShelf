<script setup >
import { store } from "../store"
import router from '../router';
import RecipeComponent from "./RecipeComponent.vue"
import { ref } from "vue"

const awesome = ref(false)

async function handleUploadClick() {
  console.log(store.loggedIn)
  await router.push('/upload')
}

async function handleReceiptClick() {
  console.log(store.loggedIn)
  await router.push('/receipt') 
}

async function handleListClick() {
  console.log(store.loggedIn)
  await router.push('/shoppinglist') 
}

function toggle() {
    test.value = !test.value
    console.log("hi")
}

</script>


<template>
  <div class="m-2 lg:m-0 lg:flex lg:flex-col lg:items-start lg:justify-between">
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
        Welcome Back, {{store.user.name}}!
      </h2>
    </div>
    <button @click=handleUploadClick class="w-full max-h-32 bg-indigo-500 px-4
        grid place-content-center grid-cols-2 mt-8 mb-8 rounded-md group
        hover:scale-105 hover:shadow-md">
      <div class="flex flex-col align-middle justify-center">
        <h2 class="text-white sm:text-xl text-left font-bold">
          Add New Receipts
        </h2>
        <p class="text-xs text-white text-left font-thin sm:text-sm">
          Add your receipts to find new recipes and track habits
        </p>
      </div>
      <div class="flex pb-8 h-48 align-center justify-center">
        <image class="group-hover:scale-110" src="/assets/receipt.png"/>
      </div>
    </button>

    <button @click=handleListClick class="w-full max-h-32 bg-sky-500 px-4
        grid place-content-center grid-cols-2 mt-8 mb-8 rounded-md group
        hover:scale-105 hover:shadow-md">
      <div class="flex flex-col align-middle justify-center">
        <h2 class="text-white sm:text-xl text-left font-bold">
          View Shopping List
        </h2>
        <p class="text-xs text-white text-left font-thin sm:text-sm">
          See what you need to buy from Kroger
        </p>
      </div>
      <div class="flex pb-8 h-48 align-center justify-center">
        <image class="group-hover:scale-110" src="/assets/shoplist.png"/>
      </div>
    </button>

    <RecipeComponent/>

    <button @click=handleReceiptClick class="w-full max-h-32 bg-lime-500 px-4 grid 
        place-content-center grid-cols-3 mt-12 mb-16 sm:mb-8 rounded-md
        hover:scale-105 hover:shadow-md group">
      <div class="flex pb-8 h-48 align-center justify-start">
        <image class="group-hover:scale-110" src="/assets/history.png"/>
      </div>
      <div class="flex flex-col align-start justify-center col-span-2">
        <h2 class="text-white sm:text-xl text-left font-bold">
          Your Receipt History
        </h2>
        <p class="text-xs text-white text-left font-thin sm:text-sm">
          View trends, and generate shopping lists from previous receipts
        </p>
      </div>
    </button>


  </div>
</template>
