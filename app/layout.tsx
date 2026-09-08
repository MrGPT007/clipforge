import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClipForge Studio — Make your next video",
  description: "Turn stories into motion videos with your own instructions, models and voice.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
