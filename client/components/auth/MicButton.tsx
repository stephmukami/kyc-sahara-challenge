"use client";

interface MicButtonProps {
  isListening: boolean;
  disabled?: boolean;
  onClick: () => void;
  hint?: string;
}

export function MicButton({ isListening, disabled, onClick, hint }: MicButtonProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <button
        type="button"
        onClick={onClick}
        disabled={disabled}
        aria-label={isListening ? "Stop listening" : "Start voice input"}
        className={`flex h-16 w-16 items-center justify-center rounded-full text-white shadow-lg transition-transform disabled:cursor-not-allowed disabled:opacity-40 ${
          isListening ? "scale-110 bg-indigo-500 animate-pulse" : "bg-indigo-600 hover:bg-indigo-500"
        }`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="h-7 w-7"
        >
          <path d="M12 14a3 3 0 0 0 3-3V6a3 3 0 1 0-6 0v5a3 3 0 0 0 3 3Z" />
          <path d="M19 11a1 1 0 1 0-2 0 5 5 0 0 1-10 0 1 1 0 1 0-2 0 7 7 0 0 0 6 6.93V20H9a1 1 0 1 0 0 2h6a1 1 0 1 0 0-2h-2v-2.07A7 7 0 0 0 19 11Z" />
        </svg>
      </button>
      {hint && (
        <span className="text-[11px] font-medium uppercase tracking-wide text-zinc-400">
          {hint}
        </span>
      )}
    </div>
  );
}
