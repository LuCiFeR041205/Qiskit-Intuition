import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Qiskit Intuition — Learn quantum computing",
  description:
    "A focused quantum computing course with an interactive circuit simulator and context-aware Qiskit code coach.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
