import speech_recognition as sr

def escuchar_wake_word():
    r = sr.Recognizer()
    # Probamos con el indice 1 (Realtek). Si no capta nada, probaremos con 5 o 12.
    mic = sr.Microphone(device_index=1)

    with mic as source:
        print("\n[Inicializando hardware de audio...]")
        r.adjust_for_ambient_noise(source, duration=1)
        print("\033[36m[J.A.R.V.I.S. A LA ESCUCHA] Di 'Hola Jarvis' para activar.\033[0m\n")

        while True:
            try:
                audio = r.listen(source, timeout=None, phrase_time_limit=3)
                print(" > [Procesando audio captado...]")
                
                texto = r.recognize_google(audio, language="es-UY").lower()
                print(f" > Escuche: '{texto}'")
                
                if "jarvis" in texto:
                    print("\033[1;32m[SISTEMA DESPERTADO] Si, Alejandro. ¿Cuales son sus ordenes?\033[0m")
                    break
                    
            except sr.UnknownValueError:
                print(" > [Audio detectado pero incomprensible]")
            except sr.RequestError as e:
                print(f"[Error de red al transcribir: {e}]")
            except Exception as e:
                print(f"[Otro error: {e}]")

if __name__ == "__main__":
    escuchar_wake_word()