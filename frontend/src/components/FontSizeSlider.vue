<template>
  <div class="font-size-slider" role="region" aria-label="Schriftgröße und Anzeigemodus">
    <label for="fontSizeSlider">Schriftgröße: </label>
    <input
      id="fontSizeSlider"
      type="range"
      min="12"
      max="36"
      v-model.number="fontSize"
      @input="updateFontSize"
    />
    <label for="themeSelect">Modus: </label>
    <select id="themeSelect" v-model="theme" @change="updateTheme">
      <option value="system">System</option>
      <option value="light">Hell</option>
      <option value="dark">Dunkel</option>
      <option value="high-contrast">Hoher Kontrast</option>
    </select>
  </div>
</template>

<script>
export default {
  name: "FontSizeSlider",
  data() {
    return {
      fontSize: 16,
      theme: "system"
    };
  },
  mounted() {
    // Schriftgröße
    const cookieFontSize = this.getCookie("fontSize");
    if (cookieFontSize) {
      this.fontSize = Number(cookieFontSize);
      this.applyFontSize();
    } else {
      this.setCookie("fontSize", this.fontSize, 365);
    }
    // Theme
    const cookieTheme = this.getCookie("theme");
    if (cookieTheme) {
      this.theme = cookieTheme;
    } else {
      this.theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      this.setCookie("theme", this.theme, 365);
    }
    this.applyTheme();
    // System-Änderungen
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", e => {
      if (this.theme === "system") {
        this.theme = e.matches ? "dark" : "light";
        this.applyTheme();
      }
    });
  },
  methods: {
    updateFontSize() {
      this.applyFontSize();
      this.setCookie("fontSize", this.fontSize, 365);
    },
    applyFontSize() {
      document.documentElement.style.fontSize = this.fontSize + "px";
    },
    updateTheme() {
      this.setCookie("theme", this.theme, 365);
      this.applyTheme();
    },
    applyTheme() {
      let t = this.theme;
      if (t === "system") {
        t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      document.documentElement.setAttribute("data-theme", t);
    },
    setCookie(name, value, days) {
      let expires = "";
      if (days) {
        const date = new Date();
        date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
        expires = "; expires=" + date.toUTCString();
      }
      document.cookie = name + "=" + (value || "") + expires + "; path=/";
    },
    getCookie(name) {
      const nameEQ = name + "=";
      const ca = document.cookie.split(";");
      for (let c of ca) {
        c = c.trim();
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length);
      }
      return null;
    }
  }
};
</script>

<style scoped>
.font-size-slider {
  position: fixed;
  bottom: 0;
  left: 0;
  background-color: rgba(255, 255, 255, 0.8);
  padding: 0.5rem;
  border-top-right-radius: 8px;
  z-index: 1000;
  display: flex;
  align-items: center;
}
.font-size-slider label {
  margin: 0 0.5rem 0 0;
  font-size: 0.8rem;
}
.font-size-slider select,
.font-size-slider input[type="range"] {
  margin-right: 1rem;
}
</style>