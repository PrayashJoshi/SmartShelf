import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/LoginView.vue';
import { store } from '../store';
import Upload from '../views/UploadView.vue';

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
    }
  ],
});

router.beforeEach((to, from) => {
  if (!store.loggedIn && to.name !== "login") {
    return { name: 'login' }
  }
})

export default router;
