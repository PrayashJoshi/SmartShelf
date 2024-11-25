<script setup>
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { shallowRef, onMounted } from 'vue';
import { Line } from 'vue-chartjs'
import { store } from '../store';

const receiptHistory = shallowRef([])

let rendered = shallowRef(false)
let data;
const getData = async () => {
  receiptHistory.value = await (
    await fetch('http://127.0.0.1:8000/api/v1/receipts/receipt_history?' + 
        new URLSearchParams({
          'user_id': store.user.user_id 
        })
    )).json()

  console.log(receiptHistory.value)

  const priceHistoryData = await (
    await fetch('http://127.0.0.1:8000/api/v1/receipts/price_history/2024?' + 
        new URLSearchParams({
          'user_id': store.user.user_id 
        })
    )).json()
  
  console.log(priceHistoryData)

  data = {
    labels: priceHistoryData.map((item) => item.month),
    datasets: [
      {
        label: 'Total',
        backgroundColor: '#f87979',
        data: priceHistoryData.map((item) => item.total)
      }
    ]
  }

  rendered.value = true
}



ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  )

const dateOnlyRegex = /^([0-9]([0-9]([0-9][1-9]|[1-9]0)|[1-9]00)|[1-9]000)(-(0[1-9]|1[0-2])(-(0[1-9]|[1-2][0-9]|3[0-1])))$/
function parseDate(dateString) {
  if (dateOnlyRegex.test(dateString)) {
    const utcDate = new Date(dateString)
    const localDate = new Date(utcDate.getTime() + utcDate.getTimezoneOffset() * 60000)
    return localDate  
  }
  return new Date
}

onMounted(()=> {
  getData()
})
</script>


<template>

    <div class="mt-4 lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
        Your Receipt History
      </h2>
    </div>

      <div v-if="rendered" class="h-96 overflow-auto">
        <ul v-for="item in receiptHistory" v-bind:key="item.receipt_id" class="grid col-span-1 grid-cols-2 gap-x-5 p-3 m-1 border-2 rounded border-gray-300 hover:border-indigo-300 ">
          <li class="text-lg font-bold col-span-2">{{ parseDate(item.add_date).toDateString() }}</li>
          <li>
            <span>Items: {{ item.items }}</span> 
          </li>
          <li class="place-self-start">
            <span>Total: ${{ item.total.toFixed(2) }}</span>
          </li>
        </ul>
      </div>

    <div class="mt-4 lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-xl font-bold leading-7 text-gray-900 sm:truncate sm:text-2xl sm:tracking-tight">
        Trends
      </h2>
    </div>

      <div class="pb-16 sm:pb-8 pt-4 ">
        <div>
          <h2 class="text-xs font-bold leading-7 text-gray-900 sm:truncate sm:text-lg sm:tracking-tight">
            Spending Habits in {{ new Date().getFullYear() }}
          </h2>
          <Line v-if="rendered" :data="data" />
        </div>
        <div>
          <h2 class="text-xs sm:text-lg font-bold leading-7 text-gray-900 sm:truncate sm:tracking-tight">
            Frequent Ingredients in {{ new Date().getFullYear() }}
          </h2>
          <Line v-if="rendered" :data="data" />
        </div>
      </div>


</template>
