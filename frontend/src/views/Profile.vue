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

<fieldset class="form-group">
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
    const selectedFile = ref(null);

    const fetchProfile = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/user/profile", {
          headers: { Authorization: "Bearer " + authStore.token }
        });
        const data = await response.json();
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
      } catch (error) {
        console.error("Fehler beim Laden des Profils:", error);
      }
    };

    const handleFileUpload = (event) => {
      selectedFile.value = event.target.files[0];
    };

    const updateProfile = async () => {
      const formData = new FormData();
      formData.append("full_name", profile.value.full_name);
      formData.append("birth_date", profile.value.birth_date);
      formData.append("short_description", profile.value.short_description);
      if (selectedFile.value) {
        formData.append("profile_picture", selectedFile.value);
      }
      formData.append("is_full_name_public", privacy.value.is_full_name_public);
      formData.append("is_age_public", privacy.value.is_age_public);
      formData.append("is_description_public", privacy.value.is_description_public);
      formData.append("is_profile_picture_public", privacy.value.is_profile_picture_public);
      try {
        const response = await fetch("http://127.0.0.1:8000/api/user/profile", {
          method: "PUT",
          headers: { Authorization: "Bearer " + authStore.token },
          body: formData
        });
        await response.json();
        alert("Profil erfolgreich aktualisiert!");
        fetchProfile();
      } catch (error) {
        console.error("Fehler beim Aktualisieren des Profils:", error);
      }
    };

    onMounted(() => {
      fetchProfile();
    });

    return { profile, privacy, handleFileUpload, updateProfile };
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
.profile textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.profile button {
  padding: 0.75rem 1rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.form-group {
  padding-left: 1rem;
  padding-right: 1rem;
}

.checkbox-group {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  padding: 0.5rem 1rem;
  column-gap: 1rem;
}

.checkbox-group label {
  margin: 0;
  white-space: nowrap;
}

.checkbox-group input[type="checkbox"] {
  width: 1.25rem;
  height: 1.25rem;
}



fieldset legend {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

</style>