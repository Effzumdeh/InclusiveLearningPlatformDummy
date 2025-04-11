import { defineStore } from "pinia";

export const useTutorialStore = defineStore("tutorial", {
  state: () => ({
    currentStep: 0,
    // Hier legen wir den aktuellen Routennamen fest – dieser wird von außen (z. B. aus App.vue) gesetzt.
    currentRoute: "",
    // Für jede Seite (Route) können eigene Schritte definiert werden
    tutorials: {
      // Beispiel für die "Home"-Seite (z. B. in App.vue, sofern hier alle globalen Elemente angezeigt werden)
      Home: [
        {
          selector: "header h1",
          message: "Willkommen auf der Lernplattform! Hier siehst du die Hauptüberschrift."
        },
        {
          selector: ".chat-btn",
          message: "Hier findest du unseren Chat-Support – klicke hier für Hilfe."
        },
        {
          selector: "#tutorial-footer",
          message: "Mit diesem Link kannst du das Tutorial später erneut aufrufen."
        }
      ],
      // Beispiel für die Kursdetail-Seite (CourseDetail.vue)
      CourseDetail: [
        {
          selector: ".back-button",
          message: "Mit diesem Button gelangst du zurück zur Übersicht."
        },
        {
          selector: "h2",
          message: "Hier wird der Titel des Kurses angezeigt."
        },
        {
          selector: ".course-content",
          message: "Das ist der Inhaltsbereich des Kurses – lies hier die wichtigsten Informationen."
        },
        {
          selector: ".comment-input",
          message: "Gib hier deinen Kommentar zum Kurs ein."
        }
      ]
      // Du kannst hier noch weitere Seiten hinzufügen, z.B. LoginRegister oder Profil, usw.
    }
  }),
  // Getter, um anhand des aktuellen Routennamens die passenden Schritte abzurufen
  getters: {
    steps: (state) => {
      return state.tutorials[state.currentRoute] || [];
    },
    totalSteps: (state) => {
      return (state.tutorials[state.currentRoute] || []).length;
    }
  },
  actions: {
    // Diese Aktion wird von außen (z.B. aus App.vue) aufgerufen, sobald sich die Route ändert.
    setRoute(currentRoute) {
      this.currentRoute = currentRoute;
      this.resetTutorial();
    },
    startTutorial() {
      this.currentStep = 0;
    },
    nextStep() {
      if (this.currentStep < this.totalSteps - 1) {
        this.currentStep++;
      }
    },
    resetTutorial() {
      this.currentStep = 0;
    }
  }
});