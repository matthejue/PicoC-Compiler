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
  a { color: #2a8892; }
  strong { color: #2a8892; }
  em { color: #e96e1a; }
  footer { color: #e96e1a; font-size: 20px; text-align: center; }
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
![_2022-02-01-09-00-02](_resources/_2022-02-01-09-00-02.png)
##### Compiler und Parser
- **Compiler:** *High-level Programm* $\xRightarrow{übersetzen}$ *Maschinencode* (ließt *ganzen* Code ein)
- **Interpreter:** *Zeile für Zeile* einlesen und *direkt ausführen*

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Concrete Syntax
- Programm als **Textrepräsentation**
- das was man Compiler als **Input** gibt
- durch **Grammatik** dargestellt:
  ```
  <code_le> = <pred_2>
  <pred_2> =  <pred_1> '||' <pred_1>
  <pred_1> = <logic_operand> '&&' <logic_operand>
  <logic_operand> = !<logic_operand> | (<code_le>) | <code_ae> | <code_ae> <cmp> <code_ae>
  <cmp> = '<' | '>' | '<=' | '>=' | '==' | '!='
  ```

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Abstract Syntax
- Darstellung **innerhalb** des Compilers
- **Abstract Syntax Tree**, der aus **Nodes** besteht und so aufgebaut ist, dass er die **Operationen**, die der Compiler ausführen muss **optimal unterstützt**
- durch **Grammatik** dargestellt:
  ```
  <code_le> = LogicBinaryOperation(<logic_operand>, <logic_connective>, <logic_operand>)
  <logic_operand> = Not(<logic_operand>) | <code_le> | ToBool(<code_ae>) | Atom(<code_ae>, <cmp>, <code_ae>)
  <logic_connective> = LAnd() | LOr()
  <cmp> = Lt() | Gt() | Le() | Ge() | Eq() | UEq()
  ```

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Lexer und Tokens
- **Lexer:** erstellt *Tokens* aus einem Stream von Symbolen, indem er lexikalische Patterns erkennt

```c
void main() {
  char var = 12 + 1;
}
```
##### $\Downarrow$
```
[<TT.IDENTIFIER>, <TT.VOID>, <TT.MAIN>, <TT.L_PAREN>, <TT.R_PAREN>,
<TT.L_BRACE>, <TT.CHAR>, <TT.IDENTIFIER>, <TT.ASSIGNMENT>, <TT.NUMBER>,
<TT.PLUS_OP>, <TT.NUMBER>, <TT.SEMICOLON>, <TT.R_BRACE>]
```

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Parser und Abstract Syntax Tree
- **Parser:** *Unwandlung* einer *Eingabe* in ein für die Weiterverarbeitung geignetes *Format*
  - *Tokens* $\xRightarrow{baut}$ *Abstract Syntax Tree*

```
[<TT.IDENTIFIER>, <TT.VOID>, <TT.MAIN>, <TT.L_PAREN>, <TT.R_PAREN>,
<TT.L_BRACE>, <TT.CHAR>, <TT.IDENTIFIER>, <TT.ASSIGNMENT>, <TT.NUMBER>,
<TT.PLUS_OP>, <TT.NUMBER>, <TT.SEMICOLON>, <TT.R_BRACE>]
```
##### $\Downarrow$
```
(stdin (void main ((char var) = (12 + 1))))
```
- **Terminalsymbole** innerhalb der Tokens dienen als Ankerpunkte zu **Unterscheidung** zweier Weggabelungen

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Abstract Sytax Tree
- **Vorrausssetzungen:**
  - Nutzlose Nodes rauswerfen
  - **einfach** den Tree **entlanglzulaufen**, **Pattern** im Baum leicht **identifizierbar**
  - Beziehung von **Operatoren** und **Operanden** soll hervorgehoben werden, **unempfindlich** gegenüber **Änderungen** der Grammatik

![_2022-02-01-11-30-44](_resources/_2022-02-01-11-30-44.png) ![_2022-02-01-11-31-23](_resources/_2022-02-01-11-31-23.png)
##### from Parse Tree to Abstract Syntax Tree
- durch Enkopplung von ursprünglicher Syntax, kommt man **Operator-Operand Model** des RETI-Assembler näher
- mehrere Sprachen in diese **Indermediate Representatio (IR)** übersetzbar

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Grammatiken in Code übersetzen
![_2022-02-01-09-49-20](_resources/_2022-02-01-09-49-20.png)
![_2022-02-01-09-50-34](_resources/_2022-02-01-09-50-34.png)
##### $\Downarrow$
![_2022-02-01-09-50-56](_resources/_2022-02-01-09-50-56.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Grammatiken in Code übersetzen

![_2022-02-01-09-52-02](_resources/_2022-02-01-09-52-02.png)
![_2022-02-01-09-52-22](_resources/_2022-02-01-09-52-22.png)
##### $\Downarrow$
![_2022-02-01-09-52-39](_resources/_2022-02-01-09-52-39.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Grammatiken in Code übersetzen
![_2022-02-01-09-54-09](_resources/_2022-02-01-09-54-09.png)
![_2022-02-01-09-53-54](_resources/_2022-02-01-09-53-54.png)
##### $\Downarrow$
![_2022-02-01-09-54-42](_resources/_2022-02-01-09-54-42.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Grammatiken in Code übersetzen
![_2022-02-01-09-55-15](_resources/_2022-02-01-09-55-15.png)
![_2022-02-01-09-55-34](_resources/_2022-02-01-09-55-34.png)
##### $\Downarrow$
![_2022-02-01-09-55-46](_resources/_2022-02-01-09-55-46.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Passes
- **Problem:** von der **abstrakten Syntax** von **PicoC** zu **abstrakter Syntax** des **RETI-Assembler** übersetzen
  - dazu das Problem in mehrere **Passes** unterteilen
  - in einem **Pass** nur **ein Ziel** erfüllen und nicht mehrere gleichzeitig
  - "passing over"

<!--small-->
![bg right:10%](_resources/background.png)

---

## Definitionen
### Passes

```
(stdin (void main ((char var) = (12 + 1))))
```
##### $\Downarrow$ alle Passes
```
LOADI SP 256;
SUBI SP 1;
LOADI ACC 12;
STOREIN SP ACC 1;
# ...
LOADI IN1 -256;
OR ACC IN1;
STORE ACC 128;
JUMP 0;
```

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
- "**else if**": `if <single-statement> else if { <statement(s)> } else { <statement(s)> }`
- **Präzidenzregeln**
- zu **großes Literal** für `char` Datentyp (**Implicit Conversion**)
- zu **großes Literal** für Parameter
- **Fehlermeldungen** und **Warnings**
- **Shell** oder **Datei** angeben
- **Config-** bzw. **Dot-Files** um Einstellungen und Historie zu speichern
- **Farbige Ausgabe** von **Fehlermeldungen**, **RETI-Code**, **Symboltabelle**, **Abstraker Syntax**, **Token** usw.

<!-- keine Seperation von von **Deklarations-** und **Anweisungsteil** -->

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Kommentare und else if
```c
void main() {
  const int var = 12;  // Einzeiliger Kommentar
  /* Mehrzeiliger Kommentar,
  der sich über mehrere Zeilen
  erstreckt */
  char var2;
  if (var > 100) {
    var2 = 2;
  } else if (/* Störender Kommentar */ var > 10)
    var2 = 1;
  else
    var2 = 0;
}
```

<!--small-->
![bg right:10%](_resources/background.png)

---

<!-- ## Funktionsumfang -->
<!-- ### Deklarations- und Anweisungsteil -->
<!-- - **Deklaration** von **Variablen** und **Konstanten** an beliebiger Stelle möglich -->
<!--  -->
<!-- ```c -->
<!-- void main() { -->
<!--   int var = 0; -->
<!--   do { -->
<!--     var = var + 1; -->
<!--   } while (var < 10); -->
<!--   int var_2 = var; -->
<!-- } -->
<!-- ``` -->
<!--  -->
<!-- [> small <] -->
<!-- ![bg right:10%](_resources/background.png) -->
<!--  -->
<!-- --- -->

## Funktionsumfang
### Präzidenzregeln
- **Konkrette Syntax:** `12 + 'c' - 1;`
  - **Astrakte Syntax:** `(12 + (99 - 1))`
- **Konkrette Syntax:** `12 * 'c' - 1;`
  - **Astrakte Syntax:** `((12 * 99) - 1)`
- **Konkrette Syntax:** `(12 < 1 + 2) * 2;`
  - **Astrakte Syntax:** `((12 < (1 + 2)) * 2)`
- **Konkrette Syntax:** `-(0 || !(12 < 3 || 3 >= 12));`
  - **Astrakte Syntax:** `(- (ToBool(0) || Not(((12 < 3) || (3 >= 12))))) `
- **Konkrette Syntax:** `12 < 1 + 2 && 12 || 0;`
  - **Astrakte Syntax:** `(((12 < (1 ^ 2)) && ToBool(12)) || ToBool(0))`

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Zu großes Literal für `char`
- Wertebereich von `char` ist zwischen $-2^7$ und $2^7-1$
  ```c
  char var = 127;    // 2^7-1 ✅
  char var_2 = 128;  // 2^7   ❌
  ```
- **Implicit Conversion** von `int` zu `char`:
    ```
      00000000_00101011_10100110_01111111
    & 00000000_00000000_00000000_11111111  // 255
      00000000_00000000_00000000_01111111
    ```
  - mit **Bitmaske** abhängig vom **"Vorzeichenbit"** an der **8ten Stelle** nach der **8ten Stelle** mit $0$en oder $1$en überschreiben
    - **Fall 1:** 8te Stelle, Wert auf rechter Seite **positiv**
      - keine **Signextension** nötig

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Zu großes Literal für `char`
- **Fall 2:** 8te Stelle, Wert auf rechter Seite **negativ**
  ```
    00000000_00000000_00000000_10000000  //  128
  v 11111111_11111111_11111111_00000000  // -256
    11111111_11111111_11111111_10000000  // -128
  ```
- Vergleich **PicoC-Compiler** und **Clang**:
  ![height:160px](_resources/_2022-02-01-07-16-38.png)
  ![height:80px](_resources/_2022-01-29-10-54-10.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Zu großes Literal für Parameter
- semantischer Wert des **Literals** zwischen $-2^{21}$ und $2^{21}-1$
![height:100px](_resources/_2022-01-28-17-10-21.png)
  ```c
  int var = 2097151;       // 2^21-1 ✅
  int var_2 = 2147483647;  // 2^31-1 ❌
  ```
- Wert des Literals durch **Shiften** erreichen:
  ```txt
    00000000_00000000_01111111_11111111  // 2^15-1
  * 00000000_00000001_00000000_00000000  // 2^16
    01111111_11111111_11111111_11111111  // 2^31-1
  ```
- aber sobald Wert des Literals $> 2^{31}-1$ **🠒** `TooLargeLiteralError`


<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
- `MismatchedTokenError`
- `NoApplicableRuleError`
- `UnknownIdentifierError`
- `RedefinitionError`
- `ConstReassignmentError`
- `TooLargeLiteralError`
- `NoMainFunctionError`
- `MoreThanOneMainFunctionError`
- `InvalidCharacterError`
- `UnclosedCharacterError`
- `NotImplementedYetError`

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### MismatchedTokenError
#### ![height:200px](_resources/_2022-02-01-05-55-02.png)
#### ![height:140px](_resources/_2022-02-01-05-58-47.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### NoApplicableRuleError
#### ![height:150px](_resources/_2022-02-01-06-07-35.png)
#### ![height:141px](_resources/_2022-02-01-06-10-04.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### UnknownIdentifierError
#### ![height:125px](_resources/_2022-02-01-06-15-22.png)
#### ![height:112px](_resources/_2022-02-01-06-17-03.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### RedefinitionError
#### ![height:250px](_resources/_2022-02-01-06-20-14.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### ConstReassignmentError
#### ![height:240px](_resources/_2022-02-01-06-23-25.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### TooLargeLiteralError
#### ![height:140px](_resources/_2022-02-01-06-29-45.png)
#### NoMainFunctionError
#### ![height:70px](_resources/_2022-02-01-06-34-34.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### MoreThanOneMainFunctionError
#### ![height:170px](_resources/_2022-02-01-06-39-57.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Fehlermeldungen
#### InvalidCharacterError
#### ![height:120px](_resources/_2022-02-01-06-41-48.png)
#### UnclosedCharacterError
#### ![height:160px](_resources/_2022-02-01-06-43-44.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Warnungen
- `ImplicitConversionWarning`

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Warnungen
#### ImplicitConversionWarning
#### ![height:270px](_resources/_2022-02-01-06-47-45.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Warnungen
#### ImplicitConversionWarning
#### ![height:270px](_resources/_2022-02-01-06-47-45_2.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Datei direkt kompilieren
```bash
./pico_c_compiler -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 -C ./code.picoc
```

### Shell
```bash
./pico_c_compiler
PicoC> compile -c -t -a -s -p -v -b 100 -e 200 -d 20 -S 2 "char bool_val = (12 < 1 + 2);";
PicoC> most_used "char bool_val = (12 < 1 + 2);";
```
- `compile <cli-options> "<code>";` (shortcut `cpl`, **multiline**)
- `most_used "<code>";` (shortcut `mu`, **multiline**)
- `color_toggle` (shortcut `ct`, **not** multiline), `-C` gets ignored
- `quit`: Shell verlassen

<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Shell
- `←`, `→`: **Cursor** links und rechs bewegen
- `↑`, `↓`: in der **Historie** vor- und rückwärts gehen
- **Multiline Command**: mit `↩` weitere Zeile, mit `;` terminieren
- `history`: ohne Argumente Liste aller ausgeführten Commands
  - `-r <command-nr>`: command mit Nr. `<command-nr>` **ausführen**
  - `-e <command-nr>`: command mit Nr. `<command-nr>` **editieren** mit `$EDITOR`
  - `-c <command-nr>`: Historie **leeren**
  - `ctrl+r` command mit substring **suchen**
- **Config Dateien** `settings.conf` und `history.json` in `~/.config/pico_c_compiler/`
  - `color_on: True` um gleich mit angeschalteten colors zu starten


<!--small-->
![bg right:10%](_resources/background.png)

---

## Funktionsumfang
### Verwendung
- **Übersichtsseite:** https://github.com/matthejue/PicoC-Compiler
- **Help-page:** https://github.com/matthejue/PicoC-Compiler/blob/master/doc/help-page.txt
  - `pico_c_compiler -h`
  - in der **Shell**: `PicoC> help compile`

### 16-farbige  Ausgabe
- (so gut wie) alle Terminals unterstützen **16 Farben ANSI-Escapesequenzen**
- **Windows Cmd-Terminal** wird speziell gehandelt

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Bachelorabeit Themenvorschlag

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Bachelorarbeit Themenvorschlag
### Umfang
- ein **optimierter Compiler**, der **Graph Coloring** nutzt, um **Locations** möglichst optimal an **Register** zuzuweisen
  - es wird vermieden **Locations** zu **Stack Positionen** zuzuweisen
    - **Registerzugriffe** schneller als **Hauptspeicherzugriffe**
    - Zugriff auf Register braucht **weniger RETI-Code** (keine `push` und `pop` Operationen)
- **Web Interface**, indem man den Compiler bedienen kann

<!--small-->
![bg right:10%](_resources/background.png)

---

## Bachelorarbeit Themenvorschlag
### Beispiel optimierter Compiler
```
SUBI SP 1;
LOADI ACC 12;
STOREIN SP ACC 1;
LOADIN SP ACC 1;
ADDI SP 1;
STORE ACC 100;
```
##### $\Downarrow$
```
LOADI ACC 12;
STORE ACC 100;
```

<!--small-->
![bg right:10%](_resources/background.png)

---

## Bachelorarbeit Themenvorschlag
### Passes eines optimalen Compilers ähnlicher Funktionalität

![_2022-02-01-12-50-39](_resources/_2022-02-01-12-50-39.png)

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Quellen

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->

---

## Quellen
### Wissenquellen
- **[1]** Parr, Terence. Language implementation patterns: create your own domain-specific and general programming languages. Pragmatic Bookshelf, 2009.
- **[2]** IU-Fall-2021. “Course Webpage for Compilers (P423, P523, E313, and E513).” Accessed January 28, 2022. https://iucompilercourse.github.io/IU-Fall-2021/.

<!--small-->
![bg right:10%](_resources/background.png)

---

## Quellen
### Bildquellen
- **[3]** “Manjaro.” Accessed January 28, 2022. https://wallpapercave.com/w/wp9774690.

<!--small-->
![bg right:10%](_resources/background.png)

---

## Quellen
### Quellen des Projekts
- alle verwendete(n) Patterns, Software, Packages usw.: https://github.com/matthejue/PicoC-Compiler/blob/master/doc/references.md

<!--small-->
![bg right:10%](_resources/background.png)

---

###### Vielen Dank für eure Aufmerksamkeit!
###### :penguin:

<!--_class: lead-->
<!--big-->
![bg right:30%](_resources/background_2.png)
<!-- _backgroundColor: #a8dec5; -->
