<script setup>
import { ref } from "vue";
import router from "../router"
import { store } from "../store"
import { digestMessage } from "../utils"

const name = ref(store.user.name)
const oldEmail = ref('')
const oldPass = ref('')
const email = ref('')
const pass = ref('')

let error = ref(false)

let handleUpdate = async () => {
  const hashedPass = await digestMessage(password.value)
  try {
    const res = await fetch('http://127.0.0.1:8000/users/verify?' + new URLSearchParams({
      'email': email.value,
      'password': hashedPass 
    }).toString())

    if (res.ok) {
      const secondRes = await
      fetch(`http://127.0.0.1:8000/users/update?id=${store.user.user_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.value,
          email: email.value,
          password: pass.value
        })
      })
    }
    else {
      console.log(error)
      error.value = true
    }
  }
  catch(e) {
    error.value = true
    console.log(e)
  }
}

</script>

<template>
  <div class="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
    <div class="lg:flex w-full lg:items-center lg:justify-between">
      <h2 class="text-2xl font-bold leading-7 mb-4 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
        Update Profile
      </h2>
    </div>

    <form class="space-y-6" @submit.prevent="handleUpdate">
      <div>
        <label for="password" class="block text-sm font-medium leading-6
          text-gray-900">
          Name
        </label>
        <div class="mt-2">
          <input id="name" v-model="name" name="name" type="text"
          autocomplete required
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
            shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
            focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
        </div>

        <label for="email" class="block text-sm font-medium leading-6 required
          text-gray-900 mt-1">Old Email address</label>
        <div class="mt-2">
          <input id="email" v-model="oldEmail" name="email" type="email"
          autocomplete="email" required
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
            shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
            focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm
            sm:leading-6">
        </div>

        <label for="password" class="block text-sm font-medium leading-6
          required text-gray-900">
          Old Password
        </label>
        <div class="mt-2">
          <input id="password" v-model="oldPass" name="email" type="email"
          autocomplete="email" required
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
            shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
            focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
        </div>

      </div>

      <div>
        <label for="email" class="block text-sm font-medium leading-6
          text-gray-900 required">New Email address</label>
        <div class="mt-2">
          <input id="email" v-model="email" name="email" type="email"
          autocomplete="email" required
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900
            shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400
            focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
        </div>

        <label for="password" class="block text-sm font-medium leading-6
          text-gray-900 required"> New Password</label>
        <div class="mt-2">
          <input id="password" v-model="pass" name="email" type="email"
          autocomplete="email" required
            class="block w-full rounded-md border-0 px-1.5 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
        </div>
      </div>
      <div>
        <button type="submit"
          class="flex w-full justify-center rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Sign
          in</button>
      </div>
    </form>
  </div>
</template>

<style>
  .required:after {
    content:" *";
    color: red;
  }
</style>
