import { useState } from "react";

type Props = {
  value: string;
  label?: string;
  className?: string;
};

export function CopyButton({ value, label = "Copy", className = "" }: Props) {
  const [copied, setCopied] = useState(false);

  async function handle() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button
      type="button"
      onClick={handle}
      aria-label={`Copy ${value}`}
      className={`rounded border border-slate-300 px-2 py-1 text-xs hover:bg-slate-100 ${className}`}
    >
      {copied ? "Copied!" : label}
    </button>
  );
}
