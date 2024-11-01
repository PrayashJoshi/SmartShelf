<script setup>
import { useObjectUrl } from '@vueuse/core'
import { onMounted, shallowRef } from 'vue'

import { store } from "../store"
import router from '../router';

const file = shallowRef()
const url = useObjectUrl(file)
const randomFoodSrc = shallowRef([])

const getData = async () => {
  let foodImageData = await fetch('https://foodish-api.com/api/')
  let imageRes = await foodImageData.json()
  randomFoodSrc.value = imageRes.image
}

function onFileChange(event) {
  file.value = event.target.files[0]
}

async function handleClick() {
  console.log(store.loggedIn)
  await router.push('/upload') 
}

onMounted(()=> getData())
</script>


<template>
  <div class="m-2 lg:m-0 lg:flex lg:flex-col lg:items-start lg:justify-between">
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
        Welcome Back, {{store.user.name}}!
      </h2>

      <!-- <input type="file" id="upload" @change="onFileChange" hidden/> -->
      <button @click=handleClick class="hidden lg:inline mt-2 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-white" for="upload">
          Upload Receipt
      </button>
    </div>

    <div class="mt-4 lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
        Recipe Of The Day
      </h2>
    </div>

    <img class="mt-4 h-64 w-full object-fill" src="https://foodish-api.com/images/pasta/pasta8.jpg"/>
  </div>
</template>