# Stackframe System V ABI

#### You:
Wie wird in C unter SystemV ABI ein Stackframe aufgebaut und abgebaut und welche Aufgabenübernimmt der caller und welche der callee? Bitte gib mir den entsprechenden x86 Assemblycode

#### ChatGPT:
Unter dem klassischen **System V ABI** für x86 gibt es klare Regeln dafür,

- wie ein Stackframe aufgebaut wird,
- welche Register erhalten bleiben müssen,
- welche Seite, also Caller oder Callee, welche Verantwortung trägt.

Ich erkläre zuerst das Prinzip für **32 Bit x86 (cdecl unter System V ABI)** und danach kurz die Unterschiede bei **x86\_64 System V ABI**.

---

# 1. Grundidee des Stackframes

Beim Funktionsaufruf wird ein neuer Bereich auf dem Stack angelegt:

```text
höhere Adressen
+------------------+
| Argumente        |
+------------------+
| Rücksprungadresse|
+------------------+ <- ESP nach CALL
| altes EBP        |
+------------------+ <- EBP
| lokale Variablen |
|                  |
+------------------+ <- ESP
niedrigere Adressen
```

---

# 2. Aufgaben von Caller und Callee (x86 32 Bit)

## Caller übernimmt

Der Caller:

1. legt Argumente auf den Stack
2. ruft `call` auf
3. räumt danach die Argumente wieder weg

Beispiel:

```c
foo(1, 2);
```

Assembly:

```asm
push 2
push 1
call foo
add esp, 8
```

Warum `8`?

2 Argumente × 4 Byte = 8 Byte.

---

## Callee übernimmt

Der Callee:

1. sichert den alten Frame Pointer
2. baut neuen Stackframe auf
3. reserviert Platz für lokale Variablen
4. restauriert alles vor `ret`

---

# 3. Vollständiges Beispiel

## C Code

```c
int add(int a, int b)
{
    int c = a + b;
    return c;
}
```

---

# 4. Typischer x86 System V Assemblycode

```asm
add:
    push ebp
    mov ebp, esp
    sub esp, 4

    mov eax, [ebp+8]
    add eax, [ebp+12]
    mov [ebp-4], eax

    mov eax, [ebp-4]

    mov esp, ebp
    pop ebp
    ret
```

---

# 5. Erklärung Zeile für Zeile

## Funktionsprolog

```asm
push ebp
```

Alten Frame Pointer sichern.

---

```asm
mov ebp, esp
```

Neuen Stackframe etablieren.

Jetzt ist `EBP` stabiler Referenzpunkt.

---

```asm
sub esp, 4
```

4 Byte Platz für lokale Variable `c`.

---

# 6. Zugriff auf Argumente

## Stacklayout

```text
[ebp+12]  b
[ebp+8]   a
[ebp+4]   Rücksprungadresse
[ebp]     altes ebp
[ebp-4]   c
```

---

```asm
mov eax, [ebp+8]
```

Lädt `a`.

---

```asm
add eax, [ebp+12]
```

Addiert `b`.

---

```asm
mov [ebp-4], eax
```

Speichert Ergebnis in lokale Variable `c`.

---

# 7. Rückgabewert

System V ABI:

- Integer Rückgabewerte kommen in `EAX`.

```asm
mov eax, [ebp-4]
```

---

# 8. Funktions-Epilog

```asm
mov esp, ebp
```

Lokale Variablen entfernen.

---

```asm
pop ebp
```

Alten Frame Pointer restaurieren.

---

```asm
ret
```

Rücksprungadresse vom Stack holen und zurückspringen.

---

# 9. Caller-Saved vs Callee-Saved Register

## Caller-Saved

Diese Register darf der Callee zerstören:

- `EAX`
- `ECX`
- `EDX`

Wenn der Caller sie behalten will, muss er selbst sichern.

---

## Callee-Saved

Diese Register muss der Callee restaurieren:

- `EBX`
- `ESI`
- `EDI`
- `EBP`

Beispiel:

```asm
push ebx
...
pop ebx
```

---

# 10. Beispiel mit Callee-Saved Register

```asm
foo:
    push ebp
    mov ebp, esp

    push ebx

    mov ebx, 42

    pop ebx

    mov esp, ebp
    pop ebp
    ret
```

---

# 11. Was macht `call` intern?

```asm
call foo
```

entspricht ungefähr:

```asm
push next_instruction
jmp foo
```

Die Rücksprungadresse landet also auf dem Stack.

---

# 12. Was macht `ret`?

```asm
ret
```

entspricht ungefähr:

```asm
pop eip
```

Also:

- Rücksprungadresse laden
- dorthin springen

---

# 13. Stackframe mit Bild

Vor Aufruf:

```text
ESP ->
```

Nach:

```asm
push 2
push 1
call add
```

Stack:

```text
| 2              |
| 1              |
| return address |
```

Nach Prolog:

```asm
push ebp
mov ebp, esp
sub esp, 4
```

Stack:

```text
| 2              | <- ebp+12
| 1              | <- ebp+8
| return address | <- ebp+4
| old ebp        | <- ebp
| c              | <- ebp-4
```

---

# 14. Moderne Compiler Optimierung

Oft wird `EBP` weggelassen:

```asm
-fomit-frame-pointer
```

Dann arbeitet der Compiler direkt mit `ESP`.

Dadurch wird ein Register frei und Code schneller.

---

# 15. x86\_64 System V ABI Unterschiede

Unter Linux/macOS x86\_64 werden die ersten Argumente in Registern übergeben:

| Argument | Register |
| -------- | -------- |
| 1        | RDI      |
| 2        | RSI      |
| 3        | RDX      |
| 4        | RCX      |
| 5        | R8       |
| 6        | R9       |

Rückgabewert:

- `RAX`

Callee-saved:

- `RBX`
- `RBP`
- `R12-R15`

---

## Beispiel x86\_64

C:

```c
long add(long a, long b)
{
    return a + b;
}
```

Assembly:

```asm
add:
    push rbp
    mov rbp, rsp

    mov rax, rdi
    add rax, rsi

    pop rbp
    ret
```

Hier braucht man oft gar keine lokalen Variablen mehr auf dem Stack.

---

# 16. Zusammenfassung

## Caller

- Argumente vorbereiten
- `call`
- caller-saved Register sichern falls nötig
- Stack aufräumen

---

## Callee

- Stackframe aufbauen
- lokale Variablen verwalten
- callee-saved Register restaurieren
- Rückgabewert setzen
- Stackframe abbauen
- `ret`

---

# 17. Klassischer kanonischer Prolog/Epilog

## Prolog

```asm
push ebp
mov ebp, esp
sub esp, N
```

---

## Epilog

```asm
mov esp, ebp
pop ebp
ret
```

Oder äquivalent:

```asm
leave
ret
```

`leave` entspricht:

```asm
mov esp, ebp
pop ebp
```


#### You:
was macht die ret instruktion?

#### ChatGPT:
Die x86-Instruction `ret` beendet eine Funktion und springt zur Rücksprungadresse zurück, die zuvor durch `call` auf den Stack gelegt wurde.

---

# 1. Grundprinzip

Ein `call` macht intern ungefähr:

```asm
push return_address
jmp function
```

Die Adresse der nächsten Instruktion wird also auf den Stack gelegt.

---

# 2. Was macht `ret`?

```asm
ret
```

macht intern ungefähr:

```asm
pop eip
```

bei 32 Bit x86.

Das bedeutet:

1. obersten Wert vom Stack holen
2. in Instruction Pointer laden
3. dorthin springen

---

# 3. Beispiel

## Caller

```asm
call foo
mov eax, 1
```

Angenommen:

```text
call foo
```

liegt bei Adresse `0x1000`.

Dann legt `call` die Adresse der nächsten Instruktion auf den Stack:

```text
0x1005
```

Stack:

```text
ESP -> 0x1005
```

Danach:

```asm
jmp foo
```

---

# 4. Im Callee

```asm
foo:
    ...
    ret
```

`ret` macht:

```asm
pop eip
```

Also:

```text
EIP = 0x1005
ESP += 4
```

Die CPU setzt die Ausführung bei:

```asm
mov eax, 1
```

fort.

---

# 5. Stackzustand

Vor `ret`:

```text
ESP -> return address
```

Nach `ret`:

```text
ESP -> nächstes Stackelement
EIP = return address
```

---

# 6. RET mit Argument

Es gibt auch:

```asm
ret 8
```

Das bedeutet:

```asm
pop eip
add esp, 8
```

Also:

1. zurückspringen
2. zusätzlich Argumente vom Stack entfernen

Das wird bei Calling Conventions verwendet, bei denen der **Callee** den Stack aufräumt, z. B.:

- stdcall (Windows)

---

# 7. Unterschied System V vs stdcall

## System V / cdecl

Caller räumt auf:

```asm
push arg2
push arg1
call foo
add esp, 8
```

Callee:

```asm
ret
```

---

## stdcall

Caller:

```asm
push arg2
push arg1
call foo
```

Callee:

```asm
ret 8
```

---

# 8. RET in x86\_64

Unter x86\_64:

```asm
ret
```

macht sinngemäß:

```asm
pop rip
```

Nur:

- 8 Byte statt 4 Byte
- Register heißt `RIP`

---

# 9. Warum `ret` sicherheitsrelevant ist

`ret` benutzt eine Adresse vom Stack.

Wenn ein Angreifer den Stack manipuliert, kann er die Rücksprungadresse überschreiben:

```text
buffer overflow
```

Dadurch entstehen:

- Return-Oriented Programming (ROP)
- Stack Smashing
- Control Flow Hijacking

Deshalb gibt es:

- Stack Canaries
- NX Bit
- Shadow Stack
- CET
- ASLR

---

# 10. Zusammenfassung

## `call`

```asm
push return_address
jmp function
```

---

## `ret`

```asm
pop instruction_pointer
```

---

## `ret N`

```asm
pop instruction_pointer
add esp, N
```

---

# 11. Minimales vollständiges Beispiel

```asm
main:
    call foo
    mov eax, 0

foo:
    mov eax, 42
    ret
```

Ablauf:

1. `call foo`
2. Rücksprungadresse auf Stack
3. Sprung nach `foo`
4. `ret`
5. Rücksprungadresse wird geladen
6. Weiter bei `mov eax, 0`
