<template>
  <div>
    <h2>Teacher Dashboard</h2>
    <p v-if="authStore.user">Willkommen, {{ authStore.user.username }}!</p>
    <p>Hier haben Sie Zugriff auf den Kurseditor und weitere Funktionen.</p>
  </div>
</template>

<script>
import { useAuthStore } from "../store/auth";
export default {
  name: "TeacherDashboard",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
};
</script>