<template>
  <div class="font-size-slider">
    <label for="fontSizeSlider">Schriftgröße: </label>
    <input
      id="fontSizeSlider"
      type="range"
      min="12"
      max="36"
      v-model.number="fontSize"
      @input="updateFontSize"
    />
  </div>
</template>

<script>
export default {
  name: "FontSizeSlider",
  data() {
    return {
      fontSize: 16, // Standardwert
    };
  },
  mounted() {
    const cookieFontSize = this.getCookie("fontSize");
    if (cookieFontSize) {
      this.fontSize = Number(cookieFontSize);
      this.applyFontSize();
    } else {
      // Standardwert im Cookie speichern, falls noch nicht gesetzt
      this.setCookie("fontSize", this.fontSize, 365);
    }
  },
  methods: {
    updateFontSize() {
      this.applyFontSize();
      // Den gewählten Wert für 365 Tage persistieren
      this.setCookie("fontSize", this.fontSize, 365);
    },
    applyFontSize() {
      document.documentElement.style.fontSize = this.fontSize + "px";
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
      for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === " ") c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
      }
      return null;
    },
  },
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
}
.font-size-slider label {
  margin-right: 0.5rem;
  font-size: 0.8rem;
}
</style>
