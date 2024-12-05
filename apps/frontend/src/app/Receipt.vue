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
import { shallowRef, onMounted, ref } from 'vue';
import { Line } from 'vue-chartjs'
import { store } from '../store';

const receiptHistory = shallowRef([])
const displayModal = ref(false)
const displayedReceipt = ref()
const displayedCost = ref()

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
    await fetch('http://127.0.0.1:8000/api/v1/receipts/price_history?' + 
        new URLSearchParams({
          'year': '2024',
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

async function display(receipt) {
  displayedReceipt.value = await (
    await fetch('http://127.0.0.1:8000/api/v1/receipts/receipt?' + 
      new URLSearchParams({
        'receipt_id': receipt.receipt_id,
        'user_id': store.user.user_id 
      })
  )).json()

  displayedCost.value = receipt.total

  console.log(displayedReceipt.value)
  toggle()
}

function toggle() {
  displayModal.value = !displayModal.value
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
        <ul v-for="item in receiptHistory" v-bind:key="item.receipt_id"
            @click="display(item)" class="grid col-span-1 grid-cols-2 gap-x-5 p-3 m-1 border-2 rounded border-gray-300 hover:border-indigo-300 ">
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
                        Receipt Total {{ displayedCost }}
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
                    <ul v-for="(item, i) in displayedReceipt"
                        :key="item.name+i">
                      <li class="grid grid-cols-3">
                          <span class="span-cols-2">{{item.name}} {{item.price}}</span>
                      </li>
                    </ul>
                </div>
            </div>
        </div>
      </div>

</template>
