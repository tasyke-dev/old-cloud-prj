import Vue from 'vue';
import VueRouter from 'vue-router';
import Home from '../views/Main.vue';
import LoadPdf from '../views/LoadPdf.vue';

Vue.use(VueRouter);

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
  },
  {
    path: '/pdf',
    name: 'LoadPdf',
    component: LoadPdf,
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
