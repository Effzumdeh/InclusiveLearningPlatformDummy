<template>
  <div class="admin-dashboard">
    <h2>Admin Dashboard</h2>
    <div v-if="authStore.user">
      <p>Willkommen, {{ authStore.user.username }}!</p>
    </div>
    <h3>Nutzerverwaltung</h3>
    <table class="users-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Nutzername</th>
          <th>Rolle</th>
          <th>Tagesziel</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.username }}</td>
          <td>{{ user.role }}</td>
          <td>{{ user.daily_target }}</td>
        </tr>
      </tbody>
    </table>
    <h3>Aggregierte Nutzungsstatistiken</h3>
    <div class="aggregated-stats">
      <p>Gesamte Lernminuten: {{ aggregatedStats.total_minutes }}</p>
      <p>Durchschnittliche Lernminuten pro Tag: {{ aggregatedStats.average_minutes }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";
export default {
  name: "AdminDashboard",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const users = ref([]);
    const aggregatedStats = ref({ total_minutes: 0, average_minutes: 0 });

    const fetchUsers = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/admin/users", {
          headers: { Authorization: "Bearer " + authStore.token },
        });
        users.value = await response.json();
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    };

    const fetchAggregatedStats = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/admin/aggregated-stats", {
          headers: { Authorization: "Bearer " + authStore.token },
        });
        aggregatedStats.value = await response.json();
      } catch (error) {
        console.error("Error fetching aggregated stats:", error);
      }
    };

    onMounted(() => {
      fetchUsers();
      fetchAggregatedStats();
    });

    return {
      authStore,
      users,
      aggregatedStats,
    };
  },
};
</script>

<style scoped>
.admin-dashboard {
  padding: 2rem;
}
.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 2rem;
}
.users-table th,
.users-table td {
  border: 1px solid #004c97;
  padding: 0.5rem;
  text-align: left;
}
.aggregated-stats p {
  font-size: 1rem;
  margin: 0.5rem 0;
}
</style>