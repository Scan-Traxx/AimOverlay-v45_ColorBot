# AimOverlay v45 🎯

Ein leistungsstarker, Python-basierter Pixel-Bot mit Echtzeit-Overlay, konfigurierbarem Key-Binding und Farberkennung. Dieses Tool wurde für maximale Benutzerfreundlichkeit und Performance entwickelt.

## ✨ Hauptfunktionen

* **Präzise Farberkennung:** Erkennt Ziele basierend auf RGB-Werten mit einstellbarer Toleranz.
* **Intelligentes Smoothing:** Verhindert ruckartige Bewegungen durch einen einstellbaren Glättungs-Algorithmus.
* **Dynamisches Overlay:**
    * **FOV-Circle:** Visualisiert den Scan-Bereich (Größe und Farbe anpassbar).
    * **ESP Marker:** Zeigt ein Rechteck auf dem erkannten Ziel an.
    * **Target Line:** Zeichnet eine Linie von der Bildschirmmitte zum Ziel.
* **Neues Key-Binding System:** Weise die Aktivierungstaste direkt im GUI zu, indem du sie einfach drückst.
* **Autofire:** Automatisches Auslösen der linken Maustaste, sobald sich das Ziel innerhalb der "Deadzone" befindet.
* **Stealth-Modus:** Das gesamte Menü lässt sich mit der `ENDE`-Taste sofort verstecken und wieder hervorholen.
* **Drag-and-Drop GUI:** Das rahmenlose Design lässt sich einfach über die Titelleiste verschieben.
* **Auto-Save:** Alle Einstellungen (Farben, Position, Hotkeys) werden automatisch in einer JSON-Datei gespeichert.

---

## 🚀 Installation & Vorbereitung

1.  **Python installieren:** Stelle sicher, dass Python 3.x installiert ist.
2.  **Abhängigkeiten installieren:**
    Öffne dein Terminal/CMD und installiere die benötigten Bibliotheken:
    ```bash
    pip install numpy mss keyboard pyautogui
    ```
3.  **Administratorrechte:** Da das Skript Tastatureingaben (`keyboard`) überwacht und die Maus steuert, muss die IDE oder die CMD-Instanz **als Administrator** ausgeführt werden.

---

## 🛠 Verwendung

### 1. Starten
Führe die Python-Datei aus. Das Overlay erscheint in der Mitte deines Bildschirms, und das Steuerungs-Menü öffnet sich an der zuletzt gespeicherten Position.

### 2. Ziel-Farbe festlegen
Es gibt zwei Wege, die Zielfarbe zu wählen:
* **Über das Menü:** Klicke auf den Button neben "Target Color" und wähle eine Farbe aus dem Paletten-Dialog.
* **Quick-Pick:** Bewege deine Maus auf das Ziel im Spiel und drücke `STRG + X`. Die Farbe unter dem Cursor wird sofort übernommen.

### 3. Tastenbelegung (Key Binding)
Klicke im Menü auf den Button unter **"Activation Key"**. Der Button färbt sich rot. Drücke nun die gewünschte Taste (z.B. `ALT`, `V` oder eine Maustaste). Die Taste wird sofort gespeichert und für den Bot genutzt.

### 4. Steuerung während des Spiels
* **Halten der Aktivierungstaste:** Der Bot sucht im FOV-Kreis nach der Zielfarbe und führt die Maus dorthin.
* **ENDE-Taste:** Minimiert das Menü in die Taskleiste / versteckt es vom Bildschirm. Erneut drücken zeigt es wieder an.
* **SAVE & EXIT:** Speichert alle aktuellen Slider-Werte und beendet das Programm sauber.

---

## ⚙️ Erläuterung der Einstellungen

| Einstellung | Beschreibung |
| :--- | :--- |
| **Smoothing** | Höhere Werte machen die Mausbewegung langsamer/weicher. Niedrige Werte sind schneller. |
| **Trigger Range (Deadzone)** | Der Bereich um das Fadenkreuz, in dem Autofire aktiv wird. |
| **Height Correction** | Verschiebt den Aim-Punkt nach oben/unten (nützlich, um von Brust auf Kopf zu zielen). |
| **Color Tolerance** | Bestimmt, wie stark die Farbe vom Zielwert abweichen darf (hilfreich bei Schatten/Licht). |
| **FOV Size** | Der Radius des Kreises, in dem der Bot nach Farben sucht. |

---

## ⚠️ Rechtlicher Hinweis
Dieses Projekt dient ausschließlich zu Bildungszwecken. Die Verwendung in Online-Spielen kann gegen die Nutzungsbedingungen verstoßen und zu einem Bann führen. Der Entwickler übernimmt keine Haftung für Missbrauch.

---

### Entwickelt mit:
* [Python](https://www.python.org/)
* [Tkinter](https://docs.python.org/3/library/tkinter.html) (GUI)
* [MSS](https://python-mss.readthedocs.io/) (Ultra-schnelle Screenshots)
