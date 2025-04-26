<template>
  <div class="user-dashboard">
    <h2>User Dashboard</h2>
    <p v-if="authStore.user">Willkommen, {{ authStore.user.username }}!</p>
  </div>
</template>

<script>
import { useAuthStore } from "../store/auth";
export default {
  name: "UserDashboard",
  setup() {
    const authStore = useAuthStore();
    return { authStore };
  },
};
</script>

<style scoped>
.user-dashboard {
  padding: 2rem;
}
</style>