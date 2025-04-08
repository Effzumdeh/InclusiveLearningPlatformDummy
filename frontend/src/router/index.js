import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import CourseDetail from "../views/CourseDetail.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/course/:courseId",
    name: "CourseDetail",
    component: CourseDetail,
  },
  {
    path: "/editor",
    name: "CourseEditor",
    component: () => import("../views/CourseEditor.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;