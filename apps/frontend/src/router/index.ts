import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import { store } from '../store';
import Upload from '../views/UploadView.vue';
import NewUser from '../views/NewUserView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/upload',
      name: 'upload',
      component: Upload
    },
    {
      path: '/new',
      name: 'new',
      component: NewUser
    }
  ],
});

router.beforeEach((to, from) => {
  if (!store.loggedIn && (to.name !== "login" && to.name !== "new")) {
    return { name: 'login' }
  }
  if (store.loggedIn && to.name === "new") {
    return { name: 'home' }
  }

})

export default router;
