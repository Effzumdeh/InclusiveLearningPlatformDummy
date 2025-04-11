<template>
  <div class="profile-view">
    <h2>Profil von {{ profile.username }}</h2>
    <div v-if="profile.profile_picture">
      <img :src="formattedImageUrl" alt="Profilbild" class="profile-picture" />
    </div>
    <p v-if="profile.full_name"><strong>Name:</strong> {{ profile.full_name }}</p>
    <p v-if="profile.age !== null && profile.age !== undefined"><strong>Alter:</strong> {{ profile.age }} Jahre</p>
    <p v-if="profile.short_description"><strong>Beschreibung:</strong></p>
    <p>{{ profile.short_description || 'Keine Beschreibung vorhanden.' }}</p>
    <p><strong>Punkte:</strong> {{ profile.points }}</p>
  </div>
</template>

<script>
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
export default {
  name: "ProfileView",
  setup() {
    const route = useRoute();
    const profile = ref({});
    const userId = route.params.user_id;

    const fetchProfile = async () => {
      try {
        const response = await fetch(`http://127.0.0.1:8000/api/user/${userId}/public-profile`);
        profile.value = await response.json();
      } catch (error) {
        console.error("Fehler beim Laden des Profils:", error);
      }
    };

    onMounted(() => {
      fetchProfile();
    });
    
    const formattedImageUrl = computed(() => {
      if (profile.value.profile_picture) {
        let path = profile.value.profile_picture.replace(/^\/+/, '');
        return `http://127.0.0.1:8000/${path}`;
      }
      return "";
    });
    
    return { profile, formattedImageUrl };
  },
};
</script>

<style scoped>
.profile-view {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.profile-view h2 {
  text-align: center;
}
.profile-picture {
  display: block;
  max-width: 200px;
  margin: 0 auto 1rem;
  border-radius: 50%;
}
</style>