<script setup >
import { store } from "../store"
import router from '../router';

async function handleUploadClick() {
  console.log(store.loggedIn)
  await router.push('/upload') 
}

async function handleReceiptClick() {
  console.log(store.loggedIn)
  await router.push('/receipt') 
}
</script>


<template>
  <div class="m-2 lg:m-0 lg:flex lg:flex-col lg:items-start lg:justify-between">
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
        Welcome Back, {{store.user.name}}!
      </h2>

      <!-- <input type="file" id="upload" @change="onFileChange" hidden/> -->
    </div>
    <!-- <button @click=handleClick class="hidden lg:inline mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white" for="upload">
      Upload Receipt
    </button> -->

    <button @click=handleUploadClick class="w-full max-h-32 bg-indigo-500 px-4 grid place-content-center grid-cols-2 mt-8 mb-8 rounded-md hover:bg-indigo-400">
      <div class="flex flex-col align-middle justify-center">
        <h2 class="text-white sm:text-xl text-left font-bold">
          Add New Receipts
        </h2>
        <p class="text-xs text-white text-left font-thin sm:text-sm">
          Add your receipts to find new recipes and track habits
        </p>
      </div>
      <div class="flex pb-8 h-48 align-center justify-center">
        <image src="/assets/receipt.png"/>
      </div>
    </button>

    <div class="mt-4 lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
        Recipes For You
      </h2>
    </div>


    <div class="mt-4 flex gap-1 overflow-x-scroll max-w-full no-scrollbar">
      <div class="min-w-52 sm:w-64 h-72 border-2 rounded-md">
        <h2>Title</h2>
      </div>
      <div class="min-w-52 sm:w-64 h-72 border-2 rounded-md">
        <h2>Title</h2>
      </div>
      <div class="min-w-52 sm:w-64 h-72 border-2 rounded-md">
        <h2>Title</h2>
      </div>
      <div class="min-w-52 sm:w-64 h-72 border-2 rounded-md">
        <h2>Title</h2>
      </div>
      <div class="min-w-52 sm:w-64 h-72 border-2 rounded-md">
        <h2>Title</h2>
      </div>
    </div>

    <button @click=handleReceiptClick class="w-full max-h-32 bg-lime-500 px-4 grid place-content-center grid-cols-3 mt-12 mb-16 sm:mb-8 rounded-md hover:bg-lime-400">
      <div class="flex pb-8 h-48 align-center justify-start">
        <image src="/assets/history.png"/>
      </div>
      <div class="flex flex-col align-start justify-center col-span-2">
        <h2 class="text-white sm:text-xl text-left font-bold">
          Your Receipt History
        </h2>
        <p class="text-xs text-white text-left font-thin sm:text-sm">
          View your receipts to learn about trends
        </p>
      </div>
    </button>


  </div>
</template>
