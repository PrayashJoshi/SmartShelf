<script setup lang="ts">
import { ref } from "vue";
import router from "../router"
import { User, store } from "../store"

defineProps<{
  title: string;
}>();
const email = ref('')

let handleLogin = async (e: Event) => {
  e.preventDefault()

  try {
    const res = await fetch('http://127.0.0.1:8000/users/verify?' + new URLSearchParams({
      'email': email.value
    }).toString())

    if (res.ok) {
      store.loggedIn = true
      let data: User = await res.json()
      store.user = data
      await router.push('/')
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
        Sign in to your account
      </h2>
    </div>

    <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
      <form class="space-y-6" @submit="handleLogin">
        <div>
          <label for="email" class="block text-sm font-medium leading-6 text-gray-900">Email address</label>
          <div class="mt-2">
            <input id="email" v-model="email" name="email" type="email" autocomplete="email"
              class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
          </div>
        </div>
        <div>
          <button type="submit"
            class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Sign
            in</button>
        </div>
      </form>

      <p class="mt-10 text-center text-sm text-gray-500">
        Not a member?
        <a href="/new" class="font-semibold leading-6 text-indigo-600 hover:text-indigo-500">Create an Account</a>
      </p>
    </div>
  </div>
</template>