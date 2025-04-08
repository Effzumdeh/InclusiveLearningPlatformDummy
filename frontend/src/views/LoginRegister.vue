<template>
  <div class="auth-container">
    <h2>Login / Registrierung</h2>
    <div class="tabs">
      <button :class="{ active: activeTab === 'login' }" @click="activeTab = 'login'">Login</button>
      <button :class="{ active: activeTab === 'register' }" @click="activeTab = 'register'">Registrierung</button>
    </div>
    <div v-if="activeTab === 'login'" class="form-container">
      <h3>Login</h3>
      <form @submit.prevent="handleLogin">
        <label for="identifier">Nutzername</label>
        <input id="identifier" v-model="loginForm.identifier" required /><br>
        <label for="password">Passwort</label>
        <input id="password" type="password" v-model="loginForm.password" required /><br>
        <button type="submit">Anmelden</button>
      </form>
      <p class="forgot" @click="forgotPassword">Passwort/PIN vergessen?</p>
    </div>
    <div v-if="activeTab === 'register'" class="form-container">
      <h3>Registrierung</h3>
      <form @submit.prevent="handleRegister">
        <label for="username">Nutzername</label>
        <input id="username" v-model="registerForm.username" required /><br>
        <label for="passwordReg">Passwort</label>
        <input id="passwordReg" type="password" v-model="registerForm.password" required /><br>
        <button type="submit">Registrieren</button>
      </form>
    </div>
    <div class="error" v-if="errorMessage">{{ errorMessage }}</div>
  </div>
</template>

<script>
import { ref } from "vue";
import { useAuthStore } from "../store/auth";
import { useRouter } from "vue-router";

export default {
  name: "LoginRegister",
  setup() {
    const authStore = useAuthStore();
    const router = useRouter();
    const activeTab = ref("login");
    const loginForm = ref({ identifier: "", password: "" });
    const registerForm = ref({ username: "", password: "" });
    const errorMessage = ref("");

    const handleLogin = async () => {
      errorMessage.value = "";
      try {
        await authStore.login(loginForm.value.identifier, loginForm.value.password);
        router.push("/");
      } catch (error) {
        errorMessage.value = "Login fehlgeschlagen.";
      }
    };

    const handleRegister = async () => {
      errorMessage.value = "";
      try {
        await authStore.register(registerForm.value.username, registerForm.value.password);
        router.push("/");
      } catch (error) {
        errorMessage.value = "Registrierung fehlgeschlagen.";
      }
    };

    const forgotPassword = () => {
      alert("Diese Funktion ist derzeit simuliert. Bitte wenden Sie sich an den Support.");
    };

    return {
      activeTab,
      loginForm,
      registerForm,
      errorMessage,
      handleLogin,
      handleRegister,
      forgotPassword,
    };
  },
};
</script>

<style scoped>
.auth-container {
  max-width: 400px;
  margin: 2rem auto;
  padding: 1rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.tabs {
  display: flex;
  justify-content: space-around;
  margin-bottom: 1rem;
}
.tabs button {
  flex: 1;
  padding: 0.5rem;
  background-color: #eeeeee;
  border: 1px solid #004c97;
  cursor: pointer;
}
.tabs button.active {
  background-color: #004c97;
  color: white;
}
.form-container {
  display: flex;
  flex-direction: column;
}
.form-container label {
  margin-top: 0.5rem;
}
.form-container input {
  padding: 0.5rem;
  margin-top: 0.25rem;
  border: 1px solid #004c97;
  border-radius: 4px;
}
.form-container button {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #004c97;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.forgot {
  margin-top: 0.5rem;
  color: blue;
  cursor: pointer;
}
.error {
  color: red;
  margin-top: 1rem;
  text-align: center;
}
</style>