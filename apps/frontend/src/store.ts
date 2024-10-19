import { reactive } from "vue";

export type User = {
  id: number,
  name: string,
  email: string
}

export const store = reactive({
  loggedIn: false,
  user: {} as User
});