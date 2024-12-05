<script setup>

  import { shallowRef, onMounted, ref } from "vue"
  import { store } from '../store';

  const items = shallowRef([])
  const total = ref(0)

  async function getData () {
    items.value = await (
      await
      fetch(`http://127.0.0.1:8000/api/v1/recipes/${store.user.user_id}/shopping-list-user`
    )).json()

    console.log(items.value)
    items.value.forEach((item) => {
      console.log(item.price)
      total.value += item.price
    })
    total.value = total.value.toFixed(2)
    console.log(total.value)
  }

  async function clear() {
    const res = await fetch('http://localhost:8000/api/v1/recipes/clear_list', {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: store.user.user_id,
        recipe_id: 0 
      }),
    })
    if (res.ok) {
      items.value = []
      total.value = 0
    }


  }

  onMounted(() => getData())

</script>


<template>
  <h2 class="text-black sm:text-2xl text-left font-bold">
    Your Shopping List
  </h2>
  <table class="table-auto overflow-x-scroll w-1/2">
    <tr v-for="(item, i) in items" :key="item.ingredient_name+i">
      <td> 
        <input id="default-checkbox" type="checkbox" value="" class="w-4 h-4
        text-grey-600 bg-u-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black truncate">{{item.ingredient_name}}</span>
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black">{{item.quantity}}</span>
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black">{{item.measurement_unit}}</span>
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black truncate">{{item.category}}</span>
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black truncate">{{item.product_name}}</span>
      </td>
      <td> 
        <span for="default-checkbox" class="ms-2 text-sm font-medium
          text-black">{{item.price}}</span>
      </td>
    </tr>
  </table>

  <h2 class="text-black sm:text-lg text-left font-bold">
    Total: {{total}}
  </h2>

  <button class="text-red-500" @click="clear">Clear All</button>

</template>
