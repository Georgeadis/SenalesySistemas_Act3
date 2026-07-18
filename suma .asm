section .data
    ; Mensajes para interactuar con el usuario
    msg1 db "Introduce el primer numero (0-9): ", 0
    len1 equ $ - msg1
    
    msg2 db "Introduce el segundo numero (0-9): ", 0
    len2 equ $ - msg2
    
    msg_res db "El resultado de la suma es: ", 0
    len_res equ $ - msg_res

section .bss
    ; Espacio reservado para almacenar la entrada del teclado y el resultado
    num1 resb 2      ; Almacena el primer carácter + enter
    num2 resb 2      ; Almacena el segundo carácter + enter
    res  resb 2      ; Almacena el carácter del resultado + enter

section .text
    global _start

_start:
    ; 1. Pedir el primer número
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg1       ; dirección de msg1
    mov rdx, len1       ; longitud
    syscall

    ; 2. Leer el primer número desde el teclado
    mov rax, 0          ; sys_read (leer entrada)
    mov rdi, 0          ; stdin (teclado)
    mov rsi, num1       ; dónde guardar la respuesta
    mov rdx, 2          ; leer 2 bytes (el número y el 'Enter')
    syscall

    ; 3. Pedir el segundo número
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg2       ; dirección de msg2
    mov rdx, len2       ; longitud
    syscall

    ; 4. Leer el segundo número desde el teclado
    mov rax, 0          ; sys_read
    mov rdi, 0          ; stdin
    mov rsi, num2       ; dónde guardar la respuesta
    mov rdx, 2          ; leer 2 bytes
    syscall

    ; 5. Proceso de la Suma Lógica
    ; Cuando el usuario teclea '3', la computadora recibe el valor ASCII 51.
    ; Para sumar los valores reales, debemos restar 48 (valor de '0' en ASCII).
    
    mov al, [num1]      ; Mover el carácter del primer número a 'al'
    sub al, 48          ; Convertir de ASCII a número real (Ej: '3' -> 3)
    
    mov bl, [num2]      ; Mover el carácter del segundo número a 'bl'
    sub bl, 48          ; Convertir de ASCII a número real (Ej: '4' -> 4)
    
    add al, bl          ; Sumar ambos números (3 + 4 = 7)
    
    ; 6. Convertir el resultado de vuelta a ASCII para poder imprimirlo
    add al, 48          ; Convertir número real a carácter ASCII (7 -> '7')
    mov [res], al       ; Guardar el carácter en la variable 'res'

    ; 7. Mostrar el mensaje del resultado
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, msg_res
    mov rdx, len_res
    syscall

    ; 8. Mostrar el número del resultado
    mov rax, 1          ; sys_write
    mov rdi, 1          ; stdout
    mov rsi, res
    mov rdx, 1          ; imprimir solo 1 byte (el número)
    syscall

    ; 9. Imprimir un salto de línea final (\n)
    mov byte [res], 10  ; Código ASCII 10 es salto de línea
    mov rax, 1
    mov rdi, 1
    mov rsi, res
    mov rdx, 1
    syscall

    ; 10. Salida limpia del programa
    mov rax, 60         ; sys_exit
    mov rdi, 0
    syscall