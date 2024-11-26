<script setup lang="ts">
import { ref } from "vue";
import router from "../router"
import { User, store } from "../store"

defineProps<{
  title: string;
}>();
const email = ref('')

let handleLogin = async (e: Event) => {
  try {

    if (email.value === "admin@ohyeah.com") {
      store.loggedIn = true
      store.admin = true
      await router.push('/admin/dash')
    }
  }
  catch(e) {
    console.log(e)
  }
}

</script>

<template>
  <div class="flex min-h-full flex-col justify-center px-6 py-12 mt-12 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-sm">
      <h2 class="mt-10 text-center text-2xl font-bold leading-9 tracking-tight text-gray-900">
        Administrative Login
      </h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
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
            class="flex w-full justify-center rounded-md bg-red-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-red-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Sign
            in</button>
        </div>
      </form>
  </div>
  </div>
</template>
