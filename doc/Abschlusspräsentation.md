---
theme: gaia
paginate: true
<!-- backgroundColor: #ffffff -->
transition: fade
footer: Bachelorprojekt PicoC-Compiler, [juergmatth@gmail.com](juertmatth@gmail.com), Universität Freiburg Technische Fakultät
style: |
  h1 { color: #2a8892; font-size: 100px; text-align: center; }
  h6 { color: #2a8892; font-size: 80px; text-align: center; }
  h2 { color: #2a8892; font-size: 60px; text-align: left; margin-top: 0px; margin-bottom: 0px; line-height: 0px; line-height: 60px;}
  h3 { color: #e96e1a; font-size: 40px; text-align: left; margin-top: 10px; margin-bottom: 20px; line-height: 40px;}
  h4 { color: #2a8892; font-size: 30px; text-align: left; margin-top: 40px; margin-bottom: 30px; line-height: 0px; font-weight: normal; }
  h5 { color: #2a8892; font-size: 20px; text-align: center; margin-top: 0px; margin-bottom: 20px; line-height: 0px; font-weight: normal; }
  a { color: #e96e1a; }
  strong { color: #2a8892; }
  em { color: #e96e1a; }
  footer { color: #2a8892; font-size: 20px; text-align: center; }
  ul { color: #252a2f; list-style: none; font-size: 25px; margin-bottom: 0px; }
  p { color: #252a2f; list-style: none;  font-size: 25px; text-align: center; margin-top: 0px; }
  ul li::before {
    content: "\1F784";
    color: #e96e1a;
    font-size: 25px;
    font-weight: bold;
    display: inline-block;
    width: 1em;
    margin-left: -1em;
  }
  section::after {
      color: #e96e1a;
      font-weight: bold;
      text-shadow: 0 0 5px #000;
  }
  code {
    background: #FCBB69;
    color: #282e33;
  }
  :root {
    --color-background: #ffffff;
    --color-foreground: #a8dec5;
    --color-highlight: #F96;
    --color-dimmed: #6a6458;
  }
  .hljs-number {
    color: #2a8892;
  }
  .hljs-keyword {
    color: #e96e1a;
  }
  .hljs-comment {
    color: #6a6458;
  }
  .hljs-params {
    color: #000000;
  }
  .hljs-title {
    color: #FCBB69;
  }

---

# Abschluss-präsentation
### Bachelorprojekt PicoC-Compiler

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)

---

###### Definitionen

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Definitionen
### Compiler und Interpreter

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Concrete Syntax

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Abstract Syntax

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Lexer und Tokens

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Parser und Abstract Syntax Tree

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Passes

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Funktionsumfang

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5 -->

---

## Funktionsumfang
### Syntax von PicoC
- nur **ein Hauptprogramm**
- nur Datentypen **int**, **char**
- Kontrollstrukturen:
  - **if**, **if-else**
  - **while**- und **do-while**-Schleifen
- **Arithmetische Ausdrücke** mit
  – binären Operatoren `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^`
  – unären Operatoren `-`, `~`
- **Logische Ausdrücke** mit
  – Vergleichsoperatoren `==`, `!=`, `<`, `>`, `<=`, `>=`
  – Logische Operatoren `!`, `&&`, `||`
- nur **einfache Zuweisungen** mit `=`

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Syntax von PicoC in der Vorlesung
![height:450px](_resources/_2022-01-25-12-36-14.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Syntax von PicoC in der Vorlesung
![height:450px](_resources/_2022-01-25-12-38-06.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Zusätze / Änderungen
- **Kommentare**
- keine Seperation von von **Deklarations-** und **Anweisungsteil**
- "**else if**": `if <single-statement> else if { <statement(s)> } else { <statement(s)> }`
- **Präzidenzregeln**
- **Implicit Conversion**
- **Fehlermeldungen** und **Warnings**
- **Shell** oder **Datei** angeben


<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Kommentare
```c
void main() {
  const int var = 12;  // Einzeiliger Kommentar
  /* Mehrzeiliger Kommentar,
  der sich über mehrere Zeilen
  erstreckt */
  char var2;
  if (var > 100)
    var2 = 2;
  else if (/* Störender Kommentar */ var > 10)
    var2 = 1;
  else
    var2 = 0;
}
```

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Präzidenzregeln
- **Konkrette Syntax:** `char var = 12 + 'c' - 1;`
  - **Astrakte Syntax:** `((char var) = (12 + (99 - 1)))`
- **Konkrette Syntax:** `int var = 12 * 'c' - 1;`
  - **Astrakte Syntax:** `((int var) = ((12 * 99) - 1))`
- `int bool_var = (12 < 1 + 2) * 2;`
- `int bool_var = -(0 || !(12 < 3 || 3 >= 12));`
- `int bool_var = 12 < 1 + 2 && 12 || 0;`
- `int bool_var = 12 || 12 < 3 && 0;`

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Implicit Conversion

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Help-page
-  sdf


<!--small-->
![bg right:10%](_resources/background.png)

---

###### Architektur

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Architektur
### Klassendiagramm

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Architektur
### Sequenzdiagramm

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Architektur
### LL(1) Recursive-Descent Lexer

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Architektur
### LL(k) Recursive-Descent Parser

- Nicht-Terminalsymbole

<!--small-->
![bg right:10%](_resources/background.png)

---

## Architektur
### Backtracking Parser

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Architektur
### Codegenerator

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Vorführung

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Vorführung
### Kompilieren einer `.picoc` Datei

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

## Vorführung
### Vergleich Fehlengen in Clang / GCC und PCC

- content

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Bachelorabeit Themenvorschlag

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

###### Quellen

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Quellen
### Wissenquellen

- source

<!--small->
![bg right:10%](_resources/background.png)

---

## Quellen
### Bildquellen

- source

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Vielen Dank für eure Aufmerksamkeit!
###### :penguin:

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->
