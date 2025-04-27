<template>
  <nav class="collapsed-sidebar" aria-label="Hauptmenü">
    <button class="burger-btn" @click="toggleMenu" :aria-expanded="menuOpen" aria-controls="sidebar-menu" aria-label="Menü ein-/ausklappen">
      ☰
    </button>
    <ul v-show="menuOpen" id="sidebar-menu" class="menu-list">
      <li v-if="canAccess('Teacher') || canAccess('Admin')">
        <router-link to="/editor" @click.native="closeMenu">Kurseditor</router-link>
      </li>
      <li>
        <router-link to="/profile" @click.native="closeMenu">Mein Profil</router-link>
      </li>
      <li v-if="canAccess('Admin')">
        <router-link to="/dashboard/admin" @click.native="closeMenu">Admin-Panel</router-link>
      </li>
      <li v-if="!authStore.user?.is_child_account">
        <router-link to="/dashboard/family" @click.native="closeMenu">Für Angehörige/Lehrkräfte</router-link>
      </li>
    </ul>
  </nav>
</template>

<script>
import { ref } from "vue";
import { useAuthStore } from "../store/auth";

export default {
  name: "CollapsedSidebar",
  setup() {
    const menuOpen = ref(false);
    const authStore = useAuthStore();

    const toggleMenu = () => {
      menuOpen.value = !menuOpen.value;
    };
    const closeMenu = () => {
      menuOpen.value = false;
    };

    const canAccess = (role) => {
      if (!authStore.user) return false;
      if (role === "Admin") return authStore.user.role === "Admin";
      if (role === "Teacher") return authStore.user.role === "Teacher" || authStore.user.role === "Admin";
      return false;
    };

    return { menuOpen, toggleMenu, closeMenu, authStore, canAccess };
  },
};
</script>

<style scoped>
.collapsed-sidebar {
  position: relative;
  display: inline-block;
}
.burger-btn {
  font-size: 1.5rem;
  background: var(--btn-bg);
  color: var(--btn-text);
  border: none;
  padding: 0.5rem 1rem;
  cursor: pointer;
  border-radius: 4px;
}
.menu-list {
  position: absolute;
  top: 2.5rem;
  left: 0;
  background: var(--bg);
  border: 1px solid var(--btn-bg);
  border-radius: 4px;
  list-style: none;
  padding: 0.5rem 0;
  margin: 0;
  min-width: 180px;
  z-index: 1000;
}
.menu-list li {
  padding: 0.5rem 1rem;
}
.menu-list li a {
  color: var(--btn-bg);
  text-decoration: none;
  font-weight: bold;
}
.menu-list li a:hover,
.menu-list li a:focus {
  text-decoration: underline;
}
</style>