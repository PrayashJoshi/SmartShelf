
<script setup lang="ts">

import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineElement,
PointElement, CategoryScale, LinearScale } from 'chart.js'
import { onMounted, ref } from 'vue';
import { Bar, Line } from 'vue-chartjs'
import { store } from '../store'

import AdminRecipe from './AdminRecipe.vue'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  )

let rendered = ref(false)
let userPrivs = ref(false)
let recipeControl = ref(false)
let userSignupData: any;
let recipeData: any;
let stats: any

async function getData() {
  // const apiData = await fetch("http://127.0.0.1:8000/api/v1/users/monthly_signups")
  // const data = await apiData.json()
  console.log(store.loggedIn)

  const data = await (
    await fetch('http://127.0.0.1:8000/api/v1/users/monthly_signups')
  ).json()

  const data2 = await (
    await fetch('http://127.0.0.1:8000/api/v1/recipes/cuisines/')
  ).json()

  const data3 = await (
    await fetch('http://127.0.0.1:8000/api/v1/users/minmax/')
  ).json()

  stats = data3[0]


  console.log(data)
  console.log(data2)
  console.log(data3)

  userSignupData = {
    labels: data.map((user:{signup_date: string}) => user.signup_date),
    datasets: [
      {
        label: 'Signups',
        backgroundColor: '#f87979',
        data: data.map((user:any) => user.signups)
      }
    ]
  }

  recipeData = {
    labels: data2.map((recipes:{cuisine_type: string}) => recipes.cuisine_type),
    datasets: [
      {
        label: 'Recipes',
        backgroundColor: '#f87979',
        data: data2.map((recipes:{cuisine_type: number}) => recipes.count)
      },
    ]
  }
  rendered.value = true

}


onMounted(async () => {
  await getData()
})
</script>


<template>
  <div class="flex w-full justify-evenly"> 
    <button 
      class="flex justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
      hover:bg-red-500 focus-visible:outline focus-visible:outline-2 mb-5
      focus-visible:outline-offset-2 focus-visible:outline-red-600"
      @click="rendered = !rendered"
      >
      {{ rendered ? 'Hide Graphs' : 'Show Graphs' }}
    </button>
    <button 
      class="flex justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
      hover:bg-red-500 focus-visible:outline focus-visible:outline-2 mb-5
      focus-visible:outline-offset-2 focus-visible:outline-red-600"
      @click="userPrivs = !userPrivs"
      >
      {{ userPrivs ? 'Hide User Control' : 'Show User Control' }}
    </button>
    <button 
      class="flex justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
      hover:bg-red-500 focus-visible:outline focus-visible:outline-2 mb-5
      focus-visible:outline-offset-2 focus-visible:outline-red-600"
      @click="recipeControl = !recipeControl "
      >
      {{ recipeControl  ? 'Hide Recipe Control' : 'Show Recipe Control' }}
    </button>
  </div>

  <section v-if="userPrivs">
    <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
       Add Admin
    </h2>
    <form class="space-y-6" @submit.prevent="handleLogin">
      <div>
        <label for="email" class="block text-sm font-medium leading-6 text-gray-900">Email address</label>
        <div class="mt-2">
          <input id="email" v-model="email" name="email" type="email" autocomplete="email"
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
        </div>
      </div>
      <div>
        <button type="submit"
          class="flex w-full justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm 
          hover:bg-red-500 focus-visible:outline focus-visible:outline-2
          focus-visible:outline-offset-2 focus-visible:outline-red-600">
          Submit
        </button>
      </div>
    </form>
  </section>

  <section :class="userPrivs ? 'mt-5' : ''"  v-if="recipeControl">
    <AdminRecipe/>
  </section>

  <section v-if="rendered" :class="recipeControl ? 'mt-5' : ''">
    <h2 class="text-lg font-bold leading-7 text-gray-900 sm:truncate
      sm:text-2xl sm:tracking-tight">
      Graphs 
    </h2>
    <h3 class="text-lg font-bold leading-7 mt-5 text-gray-900 sm:truncate sm:text-xl sm:tracking-tight">
      Monthly Users Signed Up 
    </h3>
    <p class="text-xs">Lowest User Count: {{ stats.min }}</p>
    <p class="text-xs">Highest User Count: {{ stats.max }}</p>
    <p class="text-xs">Average User Count: {{ stats.avg }}</p>
    <div class="w-full">
      <Line v-if="rendered" :data="userSignupData" />
    </div>

    <h3 v-if="rendered" class="text-lg font-bold leading-7 text-gray-900 sm:truncate sm:text-xl sm:tracking-tight">
      Recipe Cuisines Types
    </h3>
    <div class="w-full">
      <Bar v-if="rendered" :data="recipeData"/>
    </div>
  </section>
</template>
