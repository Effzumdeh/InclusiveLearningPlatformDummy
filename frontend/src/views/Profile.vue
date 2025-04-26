<template>
  <div class="profile">
    <h2>Mein Profil</h2>
    <form @submit.prevent="updateProfile" enctype="multipart/form-data">
      <div class="form-group">
        <label for="full_name">Name:</label>
        <input id="full_name" v-model="profile.full_name" type="text" />
      </div>
      <div class="form-group">
        <label for="birth_date">Geburtsdatum:</label>
        <input id="birth_date" v-model="profile.birth_date" type="date" />
      </div>
      <div class="form-group">
        <label for="short_description">Kurzbeschreibung:</label>
        <textarea id="short_description" v-model="profile.short_description"></textarea>
      </div>
      <div class="form-group">
        <label for="profile_picture">Profilbild:</label>
        <input id="profile_picture" type="file" @change="handleFileUpload" />
      </div>

      <fieldset class="form-group" v-if="!authStore.user.is_child_account">
        <legend>Öffentliche Anzeigeoptionen</legend>
        <div class="checkbox-group">
          <label for="public_name">Name öffentlich anzeigen</label>
          <input type="checkbox" v-model="privacy.is_full_name_public" id="public_name" />
        </div>
        <div class="checkbox-group">
          <label for="public_age">Alter öffentlich anzeigen</label>
          <input type="checkbox" v-model="privacy.is_age_public" id="public_age" />
        </div>
        <div class="checkbox-group">
          <label for="public_description">Kurzbeschreibung öffentlich anzeigen</label>
          <input type="checkbox" v-model="privacy.is_description_public" id="public_description" />
        </div>
        <div class="checkbox-group">
          <label for="public_picture">Profilbild öffentlich anzeigen</label>
          <input type="checkbox" v-model="privacy.is_profile_picture_public" id="public_picture" />
        </div>
      </fieldset>

      <fieldset class="form-group" v-if="!authStore.user.is_child_account">
        <legend>Seitenanzeigeoptionen</legend>
        <div class="checkbox-group">
          <label for="show_chat">KI-Assistent-Chat anzeigen</label>
          <input type="checkbox" id="show_chat" v-model="preferences.show_chat" />
        </div>
        <div class="checkbox-group">
          <label for="show_stats">Lernstatistiken anzeigen</label>
          <input type="checkbox" id="show_stats" v-model="preferences.show_stats" />
        </div>
        <div class="checkbox-group">
          <label for="show_comments">Kommentare anzeigen</label>
          <input type="checkbox" id="show_comments" v-model="preferences.show_comments" />
        </div>
        <div class="form-group">
          <label for="theme_preference">Anzeigemodus</label>
          <select id="theme_preference" v-model="preferences.theme_preference">
            <option value="system">System</option>
            <option value="light">Hell</option>
            <option value="dark">Dunkel</option>
            <option value="high-contrast">Hoher Kontrast</option>
          </select>
        </div>
      </fieldset>

      <button type="submit">Profil aktualisieren</button>
    </form>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useAuthStore } from "../store/auth";

export default {
  name: "Profile",
  setup() {
    const authStore = useAuthStore();
    const profile = ref({
      full_name: "",
      birth_date: "",
      short_description: "",
      profile_picture: ""
    });
    const privacy = ref({
      is_full_name_public: true,
      is_age_public: true,
      is_description_public: true,
      is_profile_picture_public: true
    });
    const preferences = ref({
      show_chat: true,
      show_stats: true,
      show_comments: true,
      theme_preference: "system"
    });
    const selectedFile = ref(null);

    const fetchProfile = async () => {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/user/profile", {
          headers: { Authorization: "Bearer " + authStore.token }
        });
        const data = await res.json();
        profile.value = {
          full_name: data.full_name || "",
          birth_date: data.birth_date || "",
          short_description: data.short_description || "",
          profile_picture: data.profile_picture || ""
        };
        privacy.value = {
          is_full_name_public: data.is_full_name_public,
          is_age_public: data.is_age_public,
          is_description_public: data.is_description_public,
          is_profile_picture_public: data.is_profile_picture_public
        };
        preferences.value = {
          show_chat: data.show_chat,
          show_stats: data.show_stats,
          show_comments: data.show_comments,
          theme_preference: data.theme_preference || "system"
        };
        authStore.user = { ...authStore.user, ...data };
        const t = preferences.value.theme_preference === "system"
          ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")
          : preferences.value.theme_preference;
        document.documentElement.setAttribute("data-theme", t);
      } catch (error) {
        console.error("Fehler beim Laden des Profils:", error);
      }
    };

    const handleFileUpload = (e) => {
      selectedFile.value = e.target.files[0];
    };

    const updateProfile = async () => {
      const formData = new FormData();
      formData.append("full_name", profile.value.full_name);
      formData.append("birth_date", profile.value.birth_date);
      formData.append("short_description", profile.value.short_description);
      if (selectedFile.value) {
        formData.append("profile_picture", selectedFile.value);
      }
      if (!authStore.user.is_child_account) {
        formData.append("is_full_name_public", privacy.value.is_full_name_public);
        formData.append("is_age_public", privacy.value.is_age_public);
        formData.append("is_description_public", privacy.value.is_description_public);
        formData.append("is_profile_picture_public", privacy.value.is_profile_picture_public);
        formData.append("show_chat", preferences.value.show_chat);
        formData.append("show_stats", preferences.value.show_stats);
        formData.append("show_comments", preferences.value.show_comments);
        formData.append("theme_preference", preferences.value.theme_preference);
      }
      try {
        const res = await fetch("http://127.0.0.1:8000/api/user/profile", {
          method: "PUT",
          headers: { Authorization: "Bearer " + authStore.token },
          body: formData
        });
        await res.json();
        alert("Profil erfolgreich aktualisiert!");
        await fetchProfile();
      } catch (error) {
        console.error("Fehler beim Aktualisieren des Profils:", error);
      }
    };

    onMounted(fetchProfile);

    return { authStore, profile, privacy, preferences, handleFileUpload, updateProfile };
  }
};
</script>

<style scoped>
.profile {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.profile form div, .profile fieldset {
  margin-bottom: 1rem;
}
.profile label {
  display: block;
  margin-bottom: 0.5rem;
}
.profile input,
.profile textarea,
.profile select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.checkbox-group label {
  margin: 0;
}
.profile button {
  padding: 0.75rem 1rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>