import { reactive } from "vue";

export type User = {
  user_id: number,
  name: string,
  email: string,
  admin: boolean
}

export const store = reactive({
  loggedIn: false,
  user: {} as User
});
