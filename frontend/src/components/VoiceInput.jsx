import { Mic, MicOff } from "lucide-react";
import { useEffect, useRef, useState } from "react";

function VoiceInput({ onTranscript }) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      return undefined;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results?.[0]?.[0]?.transcript;
      if (transcript) {
        onTranscript(transcript);
      }
    };
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    return () => recognition.stop();
  }, [onTranscript]);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
      return;
    }

    recognitionRef.current.start();
    setIsListening(true);
  };

  return (
    <button
      type="button"
      onClick={toggleListening}
      className="inline-flex items-center gap-2 rounded-full border border-signal/40 bg-signal/10 px-4 py-2 text-sm font-semibold text-sky-100 transition hover:border-signal hover:bg-signal/20"
    >
      {isListening ? <MicOff size={16} /> : <Mic size={16} />}
      {isListening ? "Listening..." : "Speak Query"}
    </button>
  );
}

export default VoiceInput;
