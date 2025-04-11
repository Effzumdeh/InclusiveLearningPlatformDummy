import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import CourseDetail from "../views/CourseDetail.vue";
import CourseEditor from "../views/CourseEditor.vue";
import LoginRegister from "../views/LoginRegister.vue";
import UserDashboard from "../views/UserDashboard.vue";
import TeacherDashboard from "../views/TeacherDashboard.vue";
import AdminDashboard from "../views/AdminDashboard.vue";
import Profile from "../views/Profile.vue";
import ProfileView from "../views/ProfileView.vue";

const routes = [
  {
    path: "/login",
    name: "LoginRegister",
    component: LoginRegister,
  },
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
    component: CourseEditor,
  },
  {
    path: "/dashboard/user",
    name: "UserDashboard",
    component: UserDashboard,
  },
  {
    path: "/dashboard/teacher",
    name: "TeacherDashboard",
    component: TeacherDashboard,
  },
  {
    path: "/dashboard/admin",
    name: "AdminDashboard",
    component: AdminDashboard,
  },
  {
    path: "/profile",
    name: "Profile",
    component: Profile,
  },
  {
    path: "/profile/:user_id",
    name: "ProfileView",
    component: ProfileView,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Global navigation guard: every route except LoginRegister requires login.
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  if (!token && to.name !== "LoginRegister") {
    next({ name: "LoginRegister" });
  } else {
    next();
  }
});

export default router;