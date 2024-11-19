<script setup lang="ts">

import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { onMounted } from 'vue';
import { Bar } from 'vue-chartjs'
import { ref } from 'vue';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

let users = ref();
let mounted = ref(false)
let userSignupData: any;
let userReceiptData: any;

async function getData() {
  const apiData = await fetch("http://127.0.0.1:8000/monthly_signups")
  const data = await apiData.json()
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

  console.log(mounted.value)
  console.log(users.value)
}
onMounted(async () => {
  await getData()
  mounted.value = true
})

</script>


<template>
  <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
    Monthly Users Signed Up 
  </h2>
  <Bar v-if="mounted" :data="userSignupData"/>


  <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
    Receipts Generated
  </h2>
  <Bar v-if="mounted" :data="userReceiptData"/>
</template>