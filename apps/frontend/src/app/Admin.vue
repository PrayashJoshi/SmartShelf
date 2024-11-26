<script setup lang="ts">

import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineElement,
PointElement, CategoryScale, LinearScale } from 'chart.js'
import { onMounted, ref } from 'vue';
import { Bar, Line } from 'vue-chartjs'
import { store } from '../store'

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
let userSignupData: any;
let userReceiptData: any;

async function getData() {
  // const apiData = await fetch("http://127.0.0.1:8000/api/v1/users/monthly_signups")
  // const data = await apiData.json()
  console.log(store.loggedIn)

  const data = await (
    await fetch('http://127.0.0.1:8000/api/v1/users/monthly_signups')
  ).json()

  console.log(data)
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

  userReceiptData = {
    labels: ["01, 2024", "02, 2024","03, 2024","04, 2024","05, 2024","06, 2024","07, 2024","08, 2024","09, 2024","10, 2024","11, 2024"],
    datasets: [
      {
        label: 'Receipts',
        backgroundColor: '#f87979',
        data: [9, 20, 10, 10, 12, 13, 14, 18, 17, 20, 25]
      },
    ]
  }
  rendered.value = true

}


onMounted(async () => {
  await getData()

  console.log(userSignupData)
})


</script>


<template>
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
        class="flex w-full justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
        Submit
      </button>
    </div>
  </form>

  <h2 class="text-xl font-bold leading-7 mt-5 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
    Monthly Users Signed Up 
  </h2>
  <div class="w-full">
    <Line v-if="rendered" :data="userSignupData" />
  </div>
  <!-- <Bar v-if="mounted" :data="userSignupData"/> -->

  <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
    Receipts Generated
  </h2>
  <div class="w-full">
    <Bar v-if="rendered" :data="userReceiptData"/>
  </div>

</template>
