import { reactive } from "vue";

export type User = {
  user_id: number,
  name: string,
  email: string
}

export const store = reactive({
  loggedIn: false,
  user: {} as User
});