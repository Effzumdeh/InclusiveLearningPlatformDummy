import { defineStore } from "pinia";

export const useTutorialStore = defineStore("tutorial", {
  state: () => ({
    currentStep: 0,
    // wird bei jedem Routenewechsel gesetzt
    currentRoute: "",
    tutorials: {
      Home: [
        {
          selector: "header h1",
          message:
            "Willkommen auf der Lernplattform! Hier siehst du die Hauptüberschrift."
        },
        {
          selector: ".chat-btn",
          message:
            "Hier findest du unseren Chat-Support – klicke hier für Hilfe."
        },
        {
          selector: "#tutorial-footer",
          message:
            "Mit diesem Link kannst du das Tutorial später erneut aufrufen."
        },
        {
          selector: ".all-courses-link a",
          message:
            "Unter 'Kurse' findest du den Link zur Auswahl aller Kurse."
        },
        {
          selector: "a[href='/dashboard/family']",
          message:
            "Hier gelangst du zum Dashboard für Angehörige/Lehrkräfte, um Kind-Konten zu verwalten."
        }
      ],
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
          message:
            "Das ist der Inhaltsbereich des Kurses – lies hier die wichtigsten Informationen."
        },
        {
          selector: ".quiz-component",
          message:
            "Das Quiz zeigt dir Fragen zum Kurs – wähle eine Antwort und erhalte direkt Feedback."
        },
        {
          selector: ".comment-input",
          message:
            "Gib hier deinen Kommentar zum Kurs ein und diskutiere mit anderen."
        }
      ],
      CourseEditor: [
        {
          selector: ".course-editor h2",
          message:
            "Im Kurseditor legst du neue Kurse an oder bearbeitest bestehende."
        },
        {
          selector: "#title",
          message: "Gib hier den Kurstitel ein."
        },
        {
          selector: "#shortDesc",
          message: "Füge eine kurze Beschreibung hinzu."
        },
        {
          selector: ".quill-editor",
          message:
            "Hier erstellst du den Kursinhalt mithilfe des Editor-Tools."
        },
        {
          selector: ".button-group button:first-child",
          message: "Klicke hier, um den Kurs zu speichern."
        },
        {
          selector: ".courses-table",
          message: "Unterhalb siehst du alle bestehenden Kurse."
        },
        {
          selector: ".quiz-form",
          message:
            "Falls du einen Kurs bearbeitest: Hier kannst du Quizfragen hinzufügen."
        },
        {
          selector: ".quiz-list",
          message:
            "In dieser Liste findest du alle vorhandenen Quizfragen deines Kurses."
        }
      ],
      Profile: [
        {
          selector: ".profile h2",
          message:
            "Dies ist dein Profil – passe hier deine persönlichen Informationen an."
        },
        {
          selector: "#full_name",
          message: "Trage hier deinen vollständigen Namen ein."
        },
        {
          selector: "#birth_date",
          message:
            "Wähle dein Geburtsdatum aus – dein Alter wird automatisch errechnet."
        },
        {
          selector: "#short_description",
          message: "Schreibe eine kurze Beschreibung über dich."
        },
        {
          selector: "#profile_picture",
          message: "Lade hier dein Profilbild hoch."
        },
        {
          selector: "button[type='submit']",
          message: "Klicke hier, um deine Profiländerungen zu speichern."
        }
      ],
      ProfileView: [
        {
          selector: ".profile-view h2",
          message: "Hier siehst du das öffentliche Profil eines Nutzers."
        },
        {
          selector: ".profile-picture",
          message: "Das Profilbild des Nutzers wird hier angezeigt."
        },
        {
          selector: ".profile-view p:nth-of-type(1)",
          message:
            "Der Name des Nutzers – sofern er öffentlich freigegeben ist."
        },
        {
          selector: ".profile-view p:nth-of-type(2)",
          message: "Das Alter des Nutzers, falls freigegeben."
        },
        {
          selector: ".profile-view p:nth-of-type(3)",
          message:
            "Die Kurzbeschreibung, die der Nutzer öffentlich anzeigen lässt."
        },
        {
          selector: ".profile-view p:last-child",
          message: "Die Gesamtpunktzahl des Nutzers siehst du hier."
        }
      ],
      CourseSelection: [
        {
          selector: ".course-selection h2",
          message: "Dies ist die Übersicht aller verfügbaren Kurse."
        },
        {
          selector: ".selection-table",
          message:
            "In dieser Tabelle findest du Titel und Kurzbeschreibung aller Kurse."
        },
        {
          selector: ".selection-table button",
          message:
            "Nutze die Buttons, um dich ein- oder abzumelden."
        }
      ],
      FamilyDashboard: [
        {
          selector: ".family-dashboard h2",
          message: "Willkommen im Dashboard für Angehörige/Lehrkräfte."
        },
        {
          selector: "section:nth-of-type(1) input:first-of-type",
          message:
            "Gib hier einen Nutzernamen für das neue Kind-Konto ein."
        },
        {
          selector: "section:nth-of-type(1) input[type='password']",
          message: "Wähle ein Passwort für das Kind-Konto."
        },
        {
          selector: "section:nth-of-type(1) button",
          message: "Klicken hier, um das Kind-Konto zu erstellen."
        },
        {
          selector: "section:nth-of-type(2) table",
          message:
            "Hier siehst du alle Kind-Konten mit Tages- und Wochenstatistik."
        },
        {
          selector: ".manage-courses",
          message:
            "Wähle 'Kurse verwalten', um Kurse für ein Kind auszuwählen."
        },
        {
          selector: ".modal-content",
          message:
            "In diesem Fenster passt du die Anzeigeoptionen für das Kind an."
        }
      ],
      AdminDashboard: [
        {
          selector: ".admin-dashboard h2",
          message:
            "Admin-Dashboard: Hier verwaltest du Nutzer und siehst Statistiken."
        },
        {
          selector: ".users-table",
          message:
            "Tabelle mit allen Nutzern, Rollen und ihren Tageszielen."
        },
        {
          selector: ".aggregated-stats",
          message:
            "Hier siehst du aggregierte Lernminuten aller Nutzer."
        }
      ],
      TeacherDashboard: [
        {
          selector: ".teacher-dashboard h2",
          message: "Teacher-Dashboard: Überblick und Schnellzugriff."
        },
        {
          selector: ".teacher-dashboard p:nth-of-type(1)",
          message:
            "Begrüßung mit deinem Nutzernamen und deiner Rolle."
        },
        {
          selector: ".teacher-dashboard p:nth-of-type(2)",
          message:
            "Hier findest du Verweise auf den Kurseditor und weitere Tools."
        }
      ],
      UserDashboard: [
        {
          selector: ".user-dashboard h2",
          message: "User-Dashboard: Deine persönliche Startseite."
        },
        {
          selector: ".user-dashboard p",
          message:
            "Hier wirst du begrüßt und erhältst erste Hinweise."
        }
      ]
    }
  }),
  getters: {
    steps: (state) => {
      return state.tutorials[state.currentRoute] || [];
    },
    totalSteps: (state) => {
      return (state.tutorials[state.currentRoute] || []).length;
    }
  },
  actions: {
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